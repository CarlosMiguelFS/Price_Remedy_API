class Banco_dados:
    
    def conection_data(token):
        import mysql.connector
        return mysql.connector.connect(
            host = "localhost",
            user = "root",
            password= token,
            database= "bd_pharmacy"
        )

    def create_user(name, phone, postal_code, token):
        conection = Banco_dados.conection_data(token)
        cursor = conection.cursor()


        # ========================= Analisar =============================
        # command_verif = f"select phone from user"
        # cursor.execute(command_verif)
        # data_verif = cursor.fetchall()
        # for phones in data_verif:
        #     phones_verif = str(phones).replace("('","").replace("',)","")
        #     if phone == phones_verif:
        #         print("Já existe esse contato")
        #     break

        command = f"insert into user(user, phone, postalCode) values ('{name}', '{phone}', '{postal_code}')"

        cursor.execute(command)
        conection.commit() 
        cursor.close()
        conection.close()

        return f"Usuario inserido{name}"
    
    def delete_user(id_user, phone, token):
        conection = Banco_dados.conection_data(token)
        cursor = conection.cursor()
        command = f"delete from user where iduser = '{id_user}' and phone = '{phone}'"
        
        cursor.execute(command)
        conection.commit()
        cursor.close()
        conection.close()

    def update_user(change,data,id, token):
        conection = Banco_dados.conection_data(token)
        cursor = conection.cursor()

        if change == "phone":
            command = f"update user set  phone = '{data}' where iduser = '{id}'"
        elif change =="user":
            command = f"update user set  user = '{data}' where iduser = '{id}'"
        elif change == "postalCode":
            command = f"update user set  postalCode = '{data}' where iduser = '{id}'"

        else:
            print(f"Update invalido para o {change}")
        
        cursor.execute(command)
        conection.commit()
        cursor.close()
        conection.close()

