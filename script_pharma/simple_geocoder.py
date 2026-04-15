import time
from functools import lru_cache
from typing import Dict, Optional

import requests


class SimpleGeocoder:
    """Simple geocoder with Google first and Nominatim fallback."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "MedRadar/1.0 "
                    "(Pharmacy Locator App - Contact: seu-email@exemplo.com)"
                )
            }
        )
        self.last_request_time = 0.0

    def _normalize_postal_code(self, cep: str) -> str:
        digits = "".join(ch for ch in str(cep or "") if ch.isdigit())
        if len(digits) == 8:
            return f"{digits[:5]}-{digits[5:]}"
        return digits

    def _normalize_address(
        self,
        rua: str,
        numero: str,
        bairro: str,
        cidade: str,
        estado: str,
        cep: str = "",
    ) -> str:
        parts = []

        if rua:
            rua_clean = " ".join(rua.strip().split())
            if numero:
                parts.append(f"{rua_clean}, {numero}")
            else:
                parts.append(rua_clean)

        if bairro:
            parts.append(bairro.strip())

        if cidade:
            parts.append(cidade.strip())

        if estado:
            parts.append(estado.strip())

        cep_normalizado = self._normalize_postal_code(cep)
        if cep_normalizado:
            parts.append(cep_normalizado)

        parts.append("Brasil")
        return ", ".join(parts)

    def _respect_rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < 1.0:
            time.sleep(1.0 - time_since_last)

        self.last_request_time = time.time()

    def _is_usable_precision(
        self, result: Optional[Dict], accept_geometric_center: bool = False
    ) -> bool:
        if not result:
            return False

        allowed_precisions = {
            "native",
            "rooftop",
            "point_of_interest",
            "street",
            "address_range",
        }
        if accept_geometric_center:
            allowed_precisions.add("geometric_center")

        return result.get("precision") in allowed_precisions

    def _google_confidence(self, location_type: str) -> float:
        return {
            "ROOFTOP": 1.0,
            "RANGE_INTERPOLATED": 0.9,
            "GEOMETRIC_CENTER": 0.75,
            "APPROXIMATE": 0.5,
        }.get(location_type, 0.0)

    def _google_precision(self, location_type: str) -> str:
        return {
            "ROOFTOP": "rooftop",
            "RANGE_INTERPOLATED": "address_range",
            "GEOMETRIC_CENTER": "geometric_center",
            "APPROXIMATE": "approximate",
        }.get(location_type, "unknown")

    def _infer_nominatim_precision(self, result: Dict) -> str:
        address = result.get("address", {}) or {}
        result_type = result.get("type", "")
        result_class = result.get("class", "")

        if address.get("house_number"):
            return "rooftop"

        if result_type in {
            "pharmacy",
            "hospital",
            "clinic",
            "commercial",
            "building",
            "residential",
        }:
            return "point_of_interest"

        if result_class == "amenity":
            return "point_of_interest"

        if result_type in {
            "road",
            "pedestrian",
            "residential",
            "tertiary",
            "secondary",
            "primary",
            "living_street",
        }:
            return "street"

        if result_type in {"suburb", "neighbourhood", "quarter"}:
            return "neighborhood"

        if result_type in {"city", "town", "municipality", "village", "administrative"}:
            return "city"

        return "unknown"

    def _nominatim_confidence(self, result: Dict, precision: str) -> float:
        importance = float(result.get("importance", 0) or 0)

        minimum_by_precision = {
            "rooftop": 0.95,
            "point_of_interest": 0.9,
            "street": 0.75,
            "neighborhood": 0.5,
            "city": 0.35,
            "unknown": 0.0,
        }

        return max(importance, minimum_by_precision.get(precision, 0.0))

    def _parse_nominatim_result(self, result: Dict) -> Dict:
        precision = self._infer_nominatim_precision(result)
        return {
            "lat": float(result["lat"]),
            "lon": float(result["lon"]),
            "display_name": result.get("display_name", ""),
            "importance": float(result.get("importance", 0)),
            "confidence": self._nominatim_confidence(result, precision),
            "type": result.get("type", ""),
            "class": result.get("class", ""),
            "precision": precision,
            "address": result.get("address", {}),
            "source": "nominatim",
        }

    def _geocode_google(self, address: str, api_key: str) -> Optional[Dict]:
        try:
            response = self.session.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={
                    "address": address,
                    "key": api_key,
                    "region": "br",
                    "language": "pt-BR",
                },
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()

            if payload.get("status") != "OK" or not payload.get("results"):
                return None

            result = payload["results"][0]
            geometry = result.get("geometry", {})
            location = geometry.get("location", {})
            location_type = geometry.get("location_type", "")

            return {
                "lat": float(location["lat"]),
                "lon": float(location["lng"]),
                "display_name": result.get("formatted_address", ""),
                "confidence": self._google_confidence(location_type),
                "precision": self._google_precision(location_type),
                "source": "google_geocoding",
            }
        except requests.exceptions.RequestException:
            return None
        except (KeyError, TypeError, ValueError):
            return None

    def _geocode_nominatim_structured(
        self, rua: str, numero: str, cidade: str, estado: str, cep: str = ""
    ) -> Optional[Dict]:
        try:
            self._respect_rate_limit()

            street = " ".join(rua.strip().split())
            if numero and street:
                street = f"{numero} {street}"

            params = {
                "format": "jsonv2",
                "limit": 1,
                "countrycodes": "br",
                "addressdetails": 1,
            }

            if street:
                params["street"] = street
            if cidade:
                params["city"] = cidade.strip()
            if estado:
                params["state"] = estado.strip()

            cep_normalizado = self._normalize_postal_code(cep)
            if cep_normalizado:
                params["postalcode"] = cep_normalizado

            response = self.session.get(
                "https://nominatim.openstreetmap.org/search",
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            results = response.json()

            if results:
                return self._parse_nominatim_result(results[0])

            return None
        except requests.exceptions.RequestException:
            return None
        except (KeyError, TypeError, ValueError):
            return None

    def _geocode_nominatim(self, address: str) -> Optional[Dict]:
        try:
            self._respect_rate_limit()

            response = self.session.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": address,
                    "format": "jsonv2",
                    "limit": 1,
                    "countrycodes": "br",
                    "addressdetails": 1,
                },
                timeout=10,
            )
            response.raise_for_status()
            results = response.json()

            if results:
                return self._parse_nominatim_result(results[0])

            return None
        except requests.exceptions.RequestException:
            return None
        except (KeyError, TypeError, ValueError):
            return None

    @lru_cache(maxsize=1000)
    def geocode(
        self,
        rua: str,
        numero: str,
        bairro: str,
        cidade: str,
        estado: str,
        cep: str = "",
        allow_city_fallback: bool = False,
    ) -> Optional[Dict]:
        full_address = self._normalize_address(rua, numero, bairro, cidade, estado, cep)

        structured_result = self._geocode_nominatim_structured(
            rua, numero, cidade, estado, cep
        )
        if self._is_usable_precision(structured_result):
            return structured_result

        full_result = self._geocode_nominatim(full_address)
        if self._is_usable_precision(full_result):
            return full_result

        if numero:
            address_without_number = self._normalize_address(
                rua, "", bairro, cidade, estado, cep
            )
            structured_without_number = self._geocode_nominatim_structured(
                rua, "", cidade, estado, cep
            )
            if self._is_usable_precision(structured_without_number):
                return structured_without_number

            full_without_number = self._geocode_nominatim(address_without_number)
            if self._is_usable_precision(full_without_number):
                return full_without_number

        if allow_city_fallback and cidade and estado:
            city_result = self._geocode_nominatim(
                self._normalize_address("", "", "", cidade, estado, cep)
            )
            if city_result:
                return city_result

        return None

    def geocode_with_fallback(
        self,
        rua: str,
        numero: str,
        bairro: str,
        cidade: str,
        estado: str,
        **kwargs,
    ) -> Optional[Dict]:
        cep = kwargs.get("cep", "")
        allow_city_fallback = kwargs.get("allow_city_fallback", False)
        google_api_key = kwargs.get("google_api_key")

        if google_api_key:
            google_result = self._geocode_google(
                self._normalize_address(rua, numero, bairro, cidade, estado, cep),
                google_api_key,
            )
            if self._is_usable_precision(
                google_result, accept_geometric_center=True
            ):
                return google_result

        return self.geocode(
            rua=rua,
            numero=numero,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            cep=cep,
            allow_city_fallback=allow_city_fallback,
        )


geocoder = SimpleGeocoder()
