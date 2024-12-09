from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import User
from apps.accounts.models import Employee, Customer, Address
from apps.job_management.models import Job
import json, os, random, requests


class MyOBToDjangoSync:
    def get_entity_to_func_dict(self):
        entity_func_dict = {
            "employees": self.upload_employee_data,
            "customers": self.upload_customer_data,
            "jobs": self.upload_jobs_data
        }
        return entity_func_dict

    # method to start the process of uploading data
    # into django database from json files
    def start_upload(self, entity, no_of_files):
        entity_func_dict = self.get_entity_to_func_dict()
        entity_func = entity_func_dict.get(entity)

        if not entity_func:
            raise Exception("Invalid entity")

        # get file name
        for i in range(1, no_of_files + 1):
            print(f"STARTED ============= FILE {i} ============= STARTED ")
            file_path = os.path.join(
                settings.BASE_DIR, "json_data", entity, f"part{i}.json"
            )
            with open(file_path) as f:
                data = json.load(f)
                data_records = data["Items"]
                entity_func(data_records)
            print(f"ENDED ============= FILE {i} ============= ENDED ")

    # Method to upload all entities with sequence
    def upload_all_entities(self):
        # Upload employees
        self.start_upload("employees", 1)

        # # Upload customers
        self.start_upload("customers", 1)

        # Upload jobs
        self.start_upload("jobs", 1)


    @transaction.atomic
    def upload_employee_data(self, data_records):
        for employee in data_records:
            # Random number of 3 digits
            random_number = str(random.randint(100, 999))

            # Personal details
            uid = employee["UID"]
            uri = employee["URI"]
            first_name = employee["FirstName"]
            last_name = employee["LastName"]
            is_individual = employee["IsIndividual"]
            password = "password123"
            row_version = employee["RowVersion"]
            is_active = employee["IsActive"]

            # Address fetch
            address = employee["Addresses"][0]
            street = address["Street"]
            city = address["City"]
            state = address["State"]
            post_code = address["PostCode"]
            country = address["Country"]

            # Personal details
            # Phone to be removed.
            phone1 = address["Phone1"]
            phone2 = address["Phone2"]
            phone3 = address["Phone3"]
            email = address["Email"]
            username = first_name + last_name + random_number
            username = username.replace(" ", "")

            # Create user object
            # Create address object
            # Create employee object

            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )
            address = Address.objects.create(
                street=street,
                city=city,
                state=state,
                post_code=post_code,
                country=country,
            )
            employee = Employee.objects.create(
                myob_uid=uid,
                myob_row_version=row_version,
                user=user,
                is_individual=is_individual,
                address=address,
                is_active=is_active,
                uri=uri,
            )

            print(username)

    @transaction.atomic
    def upload_customer_data(self, data_records):
        for customer in data_records:
            random_number = (
                str(random.randint(1, 9))
                + str(random.randint(1, 9))
                + str(random.randint(1, 9))
            )

            # personal details
            first_name = ""
            last_name = ""
            name = ""
            uri = customer["URI"]
            uid = customer["UID"]
            is_individual = customer["IsIndividual"]
            password = "password123"
            row_version = customer["RowVersion"]
            is_active = customer["IsActive"]
            company_name = ""
            if is_individual:
                first_name = customer["FirstName"]
                last_name = customer["LastName"]
                name = first_name + " " + last_name
            else:
                company_name = customer["CompanyName"]
                name = company_name

            # Address fetch
            address = customer["Addresses"][0]
            street = address["Street"]
            city = address["City"]
            state = address["State"]
            post_code = address["PostCode"]
            country = address["Country"]

            # Personal details
            phone1 = address["Phone1"]
            phone2 = address["Phone2"]
            phone3 = address["Phone3"]
            email = address["Email"]

            username = name + random_number
            username = username.replace(" ", "")

            # Create user object
            # Create address object
            # Create customer object

            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )
            address = Address.objects.create(
                street=street,
                city=city,
                state=state,
                post_code=post_code,
                country=country,
            )
            customer = Customer.objects.create(
                myob_uid=uid,
                myob_row_version=row_version,
                user=user,
                name=name,
                is_individual=is_individual,
                company_name=company_name,
                is_active=is_active,
                address=address,
                uri=uri,
            )

            print(username)

    @transaction.atomic
    def upload_activity_data(self, data_records):
        # running loop for each activity
        from apps.work_tracker.models import (
            ActivitySlip,
            Activity,
            IncomeAccount,
            TaxCode,
        )

        for data in data_records:
            chargeable_details = data.get("ChargeableDetails")
            income_account_data = tax_code_data = None

            # Create activity object
            activity = Activity(
                myob_uid=data.get("UID"),
                myob_row_version=data.get("RowVersion"),
                display_id=data.get("DisplayID"),
                name=data.get("Name"),
                description=data.get("Description"),
                is_active=data.get("IsActive"),
                activity_type=data.get("Type"),
                unit_of_measurement=data.get("UnitOfMeasurement"),
                status=data.get("Status"),
                uri=data.get("URI"),
            )

            if chargeable_details:
                # Create income account object and tax code object
                # if chargeable details are present
                income_account_data = chargeable_details.get(
                    "IncomeAccount", {}
                )
                tax_code_data = chargeable_details.get("TaxCode", {})

                income_account, _ = IncomeAccount.objects.get_or_create(
                    myob_uid=income_account_data.get("UID"),
                    defaults={
                        "name": income_account_data.get("Name"),
                        "display_id": income_account_data.get("DisplayID"),
                        "uri": income_account_data.get("URI"),
                    },
                )

                tax_code, _ = TaxCode.objects.get_or_create(
                    myob_uid=tax_code_data.get("UID"),
                    defaults={
                        "code": tax_code_data.get("Code"),
                        "uri": tax_code_data.get("URI"),
                    },
                )

                # Update activity object with chargeable details
                activity.use_description_on_sales = chargeable_details.get(
                    "UseDescriptionOnSales"
                )
                activity.rate = chargeable_details.get("Rate")
                activity.activity_rate_excluding_tax = chargeable_details.get(
                    "ActivityRateExcludingTax"
                )
                activity.income_account = income_account
                activity.tax_code = tax_code

            # Save activity object
            activity.save()

            # Print the created activity instance for verification
            print(activity)

    @transaction.atomic
    def upload_jobs_data(self, data_records):
        for job in data_records:
            # job details
            uid = job["UID"]
            name = job["Name"]
            number = job["Number"]
            description = job["Description"]
            row_version = job["RowVersion"]
            is_active = job["IsActive"]
            last_modified_date = job["LastModified"]
            linked_customer_obj = None
            parent_job_obj = None

            # Customer foriegnkey
            linked_customer = job["LinkedCustomer"]
            if linked_customer:
                customer_uid = linked_customer["UID"]
                customer_name = linked_customer["Name"]
                linked_customer_obj = Customer.objects.filter(
                    myob_uid=customer_uid
                ).first()

            # Parent job foreignkey
            parent_job = job["ParentJob"]
            if parent_job:
                job_uid = parent_job["UID"]
                job_name = parent_job["Name"]
                job_number = parent_job["Number"]
                parent_job_obj, created = Job.objects.get_or_create(
                    myob_uid=job_uid,
                    defaults={"name": job_name, "number": job_number},
                )

            # Create job object
            job, created = Job.objects.get_or_create(
                myob_uid=uid, defaults={"name": name, "number": number}
            )
            job_info = {
                "myob_row_version": row_version,
                "name": name,
                "number": number,
                "description": description,
                "is_active": is_active,
                "customer": linked_customer_obj,
                "parent_job": parent_job_obj,
                "last_modified_date": last_modified_date,
            }
            Job.objects.filter(myob_uid=uid).update(**job_info)

            print("job name:", job.name, job.number)

    @transaction.atomic
    def upload_payroll_categories_data(self, data_records):
        from apps.work_tracker.models import IncomeAccount, PayrollCategory

        # running loop for each payroll category
        for json_obj in data_records:
            # Extract the 'OverriddenWagesExpenseAccount' from the JSON object
            overridden_wages_expense_account_data = json_obj.get(
                "OverriddenWagesExpenseAccount"
            )
            hourly_details = json_obj.get("HourlyDetails")

            # Create or get the IncomeAccount based on the UID
            if overridden_wages_expense_account_data:
                (
                    overridden_wages_expense_account,
                    created,
                ) = IncomeAccount.objects.get_or_create(
                    myob_uid=overridden_wages_expense_account_data.get("UID"),
                    defaults={
                        "name": overridden_wages_expense_account_data.get(
                            "Name"
                        ),
                        "display_id": overridden_wages_expense_account_data.get(
                            "DisplayID"
                        ),
                        "uri": overridden_wages_expense_account_data.get(
                            "URI"
                        ),
                        # Add other fields as necessary
                    },
                )
            else:
                overridden_wages_expense_account = None

            # Create the PayrollCategory instance
            payroll_category = PayrollCategory(
                myob_uid=json_obj.get("UID"),
                myob_row_version=json_obj.get("RowVersion"),
                name=json_obj.get("Name"),
                type=json_obj.get("Type"),
                wage_type=json_obj.get("WageType"),
                stp_category=json_obj.get("StpCategory"),
                overridden_wages_expense_account=overridden_wages_expense_account,
                uri=json_obj.get("URI"),
            )

            if hourly_details:
                payroll_category.pay_rate = hourly_details.get("PayRate")
                payroll_category.regular_rate_multiplier = hourly_details.get(
                    "RegularRateMultiplier"
                )
                payroll_category.fixed_hourly_rate = hourly_details.get(
                    "FixedHourlyRate"
                )
                payroll_category.automatically_adjust_base_amounts = (
                    hourly_details.get("AutomaticallyAdjustBaseAmounts")
                )

            # Save the PayrollCategory instance
            payroll_category.save()

            # Print the created activity instance for verification
            print(payroll_category)

    @transaction.atomic
    def upload_activity_slip_data(self, data_records):
        from apps.work_tracker.models import (
            ActivitySlip,
            Activity,
            PayrollCategory,
        )

        for item in data_records:
            activity_slip = ActivitySlip(
                display_id=item.get("DisplayID"),
                myob_uid=item.get("UID"),
                myob_row_version=item.get("RowVersion"),
                date=item.get("Date"),
                unit_count=item.get("UnitCount"),
                rate=item.get("Rate"),
                adjustment_amount=item.get("AdjustmentAmount"),
                already_billed_amount=item.get("AlreadyBilledAmount"),
                adjustment_count=item.get("AdjustmentCount"),
                already_billed_count=item.get("AlreadyBilledCount"),
                notes=item.get("Notes"),
                start_stop_description=item.get("StartStopDescription"),
                start_time=item.get("StartTime"),
                end_time=item.get("EndTime"),
                elapsed_time=item.get("ElapsedTime"),
                paid_to_employee_amount=item.get("PaidToEmployeeAmount"),
                uri=item.get("URI"),
            )

            provider_data = item.get("Provider")
            customer_data = item.get("Customer")
            activity_data = item.get("Activity")
            payroll_category_data = item.get("HourlySalaryPayrollCategory")
            job_data = item.get("Job")

            if provider_data:
                provider = Employee.objects.filter(
                    myob_uid=provider_data.get("UID")
                ).first()
                activity_slip.provider = provider

            if customer_data:
                customer = Customer.objects.filter(
                    myob_uid=customer_data.get("UID")
                ).first()
                activity_slip.customer = customer

            if activity_data:
                activity = Activity.objects.filter(
                    myob_uid=activity_data.get("UID")
                ).first()
                activity_slip.activity = activity

            if job_data:
                job = Job.objects.filter(myob_uid=job_data.get("UID")).first()
                activity_slip.job = job

            if payroll_category_data:
                payroll_category = PayrollCategory.objects.filter(
                    myob_uid=payroll_category_data.get("UID")
                ).first()
                activity_slip.hourly_salary_payroll_category = payroll_category

            activity_slip.save()

            print(activity_slip)
