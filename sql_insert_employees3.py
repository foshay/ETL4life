from utils.sql_actions import insert_employees_3_sqlalchemy
from pydanticModelParsing import parseEmployees_3

if __name__ == "__main__":
    employees = parseEmployees_3()
    inserted = insert_employees_3_sqlalchemy(employees=employees)
    print(f"Inserted {inserted} employees into sqlite")