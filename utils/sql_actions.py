# pyright: reportMissingImports=false

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, create_engine, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from models.employees3 import Employee as Employee3



class Base(DeclarativeBase):
	pass


class EmployeeRecord(Base):
	__tablename__ = "employees"

	employee_id: Mapped[int] = mapped_column(Integer, primary_key=True)
	first_name: Mapped[str] = mapped_column(String, nullable=False)
	last_name: Mapped[str] = mapped_column(String, nullable=False)
	email: Mapped[str] = mapped_column(String, nullable=False)
	phone_number: Mapped[str] = mapped_column(String, nullable=False)
	employment_status: Mapped[str] = mapped_column(String, nullable=False)
	preferred_name: Mapped[str | None] = mapped_column(String, nullable=True)


class EmploymentPeriodRecord(Base):
	__tablename__ = "employment_periods"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	employee_id: Mapped[int] = mapped_column(ForeignKey("employees.employee_id"), nullable=False)
	start_date: Mapped[str] = mapped_column(String, nullable=False)
	end_date: Mapped[str | None] = mapped_column(String, nullable=True)


class JobRecord(Base):
	__tablename__ = "jobs"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	employee_id: Mapped[int] = mapped_column(ForeignKey("employees.employee_id"), nullable=False)
	job_id: Mapped[str] = mapped_column(String, nullable=False)
	pay_type: Mapped[str] = mapped_column(String, nullable=False)
	pay_value: Mapped[float] = mapped_column(Float, nullable=False)
	is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False)


class JobPeriodRecord(Base):
	__tablename__ = "job_periods"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	job_row_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
	start_date: Mapped[str] = mapped_column(String, nullable=False)
	end_date: Mapped[str | None] = mapped_column(String, nullable=True)


class LocationRecord(Base):
	__tablename__ = "locations"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	employee_id: Mapped[int] = mapped_column(ForeignKey("employees.employee_id"), nullable=False)
	location_id: Mapped[str] = mapped_column(String, nullable=False)
	start_date: Mapped[str] = mapped_column(String, nullable=False)
	end_date: Mapped[str | None] = mapped_column(String, nullable=True)


def insert_employees_3_sqlalchemy(employees: list[Employee3], sqlite_url: str = "sqlite:///employees3.db") -> int:
	engine = create_engine(sqlite_url)
	Base.metadata.create_all(engine)

	with Session(engine) as session:
		for employee in employees:
			employee_stmt = insert(EmployeeRecord).values(
				employee_id=employee.employee_id,
				first_name=employee.first_name,
				last_name=employee.last_name,
				email=employee.email,
				phone_number=employee.phone_number,
				employment_status=employee.employment_status,
				preferred_name=employee.preferred_name,
			)
			employee_upsert_stmt = employee_stmt.on_conflict_do_update(
				index_elements=[EmployeeRecord.employee_id],
				set_={
					"first_name": employee_stmt.excluded.first_name,
					"last_name": employee_stmt.excluded.last_name,
					"email": employee_stmt.excluded.email,
					"phone_number": employee_stmt.excluded.phone_number,
					"employment_status": employee_stmt.excluded.employment_status,
					"preferred_name": employee_stmt.excluded.preferred_name,
				},
			)
			session.execute(employee_upsert_stmt)

			for period in employee.employment_periods:
				existing_period = session.execute(
					select(EmploymentPeriodRecord).where(
						EmploymentPeriodRecord.employee_id == employee.employee_id,
						EmploymentPeriodRecord.start_date == period.start_date,
					)
				).scalar_one_or_none()

				if existing_period is None:
					session.add(
						EmploymentPeriodRecord(
							employee_id=employee.employee_id,
							start_date=period.start_date,
							end_date=period.end_date,
						)
					)
				else:
					existing_period.end_date = period.end_date

			for job in employee.jobs:
				job_row = session.execute(
					select(JobRecord).where(
						JobRecord.employee_id == employee.employee_id,
						JobRecord.job_id == job.job_id,
					)
				).scalar_one_or_none()

				if job_row is None:
					job_row = JobRecord(
						employee_id=employee.employee_id,
						job_id=job.job_id,
						pay_type=job.pay_type,
						pay_value=job.pay_value,
						is_primary=job.is_primary,
					)
					session.add(job_row)
					session.flush()
				else:
					job_row.pay_type = job.pay_type
					job_row.pay_value = job.pay_value

				for job_period in job.job_periods:
					existing_job_period = session.execute(
						select(JobPeriodRecord).where(
							JobPeriodRecord.job_row_id == job_row.id,
							JobPeriodRecord.start_date == job_period.start_date,
						)
					).scalar_one_or_none()

					if existing_job_period is None:
						session.add(
							JobPeriodRecord(
								job_row_id=job_row.id,
								start_date=job_period.start_date,
								end_date=job_period.end_date,
							)
						)
					else:
						existing_job_period.end_date = job_period.end_date

			for location in employee.locations:
				existing_location = session.execute(
					select(LocationRecord).where(
						LocationRecord.employee_id == employee.employee_id,
						LocationRecord.location_id == location.location_id,
						LocationRecord.start_date == location.start_date,
					)
				).scalar_one_or_none()

				if existing_location is None:
					session.add(
						LocationRecord(
							employee_id=employee.employee_id,
							location_id=location.location_id,
							start_date=location.start_date,
							end_date=location.end_date,
						)
					)
				else:
					existing_location.end_date = location.end_date

		session.commit()

	return len(employees)
