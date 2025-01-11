from django.db import models
from django.contrib.auth.models import User, Group, Permission


class TaxCode(models.Model):
    myob_uid = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    uri = models.URLField()

    def __str__(self):
        return self.code



class Address(models.Model):
    """Represents a physical address.

    The address can be associated with one or more `Employee` instances.

    Fields:
    - street: The street name and number.
    - city: The city name.
    - post_code: The postal code or ZIP code.
    - state: The state or province.
    - country: The country name.
    - phone: The phone number (up to 21 characters).
    - email: The email address which is unique.

    Methods:
    - __str__(): Returns a string representation of this Address instance.
    """

    class StateChoices(models.TextChoices):
        NEW_SOUTH_WALES = "NSW", "New South Wales"
        QUEENSLAND = "QLD", "Queensland"
        TASMANIA = "TAS", "Tasmania"
        VICTORIA = "VIC", "Victoria"
        WESTERN_AUSTRALIA = "WA", "Western Australia"
        SOUTH_AUSTRALIA = "SA", "South Australia"
        NORTHERN_TERRITORY = "NT", "Northern Territory"
        AUSTRALIAN_CAPITAL_TERRITORY = "ACT", "Australian Capital Territory"

    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    post_code = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(
        max_length=50, choices=StateChoices.choices, blank=True, null=True
    )

    def __str__(self):
        """Returns a string representation of this Address instance."""
        parts = []
        if self.street:
            parts.append(self.street)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.get_state_choice_short_format(self.state))
        if self.post_code:
            parts.append(self.post_code)
        if self.country:
            parts.append(self.country)
        parts = [part for part in parts if part]
        address = ", ".join(parts)
        return address

    def get_state_choice_short_format(self, state):
        """Returns the short format of the state."""
        for choice in self.StateChoices.choices:
            if choice[1] == state:
                return choice[0]
        return None


class Employee(models.Model):
    """Represents an employee in a company.

    Attributes:
    -   company_name (str): The name of the company the employee works for.
    -   user (User): A reference to the User instance associated with this employee.
    -   manager (Manager): A reference to the manager that this employee reports to.
    -   is_individual (bool): Indicates whether the employee is an individual contributor (as opposed to a manager).
    -   address (Address): A reference to the physical address of the employee.
    -   row_version (str): A version string used to manage concurrency conflicts.
    -   role (str): A comma-separated list of the employee's roles (e.g., 'admin,project_manager').
    -   user_permissions (QuerySet): The permissions granted to the user associated with this employee.

    Methods:
    - __str__(): Returns a string representation of this employee instance.
    """

    display_id = models.CharField(max_length=255, null=True, blank=True)
    myob_uid = models.CharField(unique=True, max_length=50, null=True, blank=True)
    myob_row_version = models.BigIntegerField(null=True, blank=True)

    company_name = models.CharField(max_length=50, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_individual = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    designation = models.CharField(max_length=50, null=True, blank=True)
    uri = models.URLField(null=True, blank=True)

    # role = models.ManyToManyField(Group, max_length=20, choices=RoleChoices.ROLE_CHOICES)
    # user_permissions = models.ManyToManyField(Permission)

    def __str__(self):
        """Returns a string representation of the Employee object, including
        the user's first and last name, and the name of the company they belong
        to."""
        return f"{self.user.first_name} {self.user.last_name}"

    def get_assigned_jobs(self):
        # """Returns a queryset of all jobs assigned to this employee."""
        # from apps.work_tracker.models import Assignment

        # return Assignment.objects.filter(employee=self)
        pass




class Customer(models.Model):
    """A model representing a customer.

    Fields:
    - address: reference to Address model
    - user: reference to User model
    - is_individual: boolean indicating whether the customer is an individual
    - is_active: boolean indicating whether the customer is active
    - row_version: character field for row version
    - selling_details_sale_type: character field for sale type details
    - selling_details_invoice_delivery: character field for invoice delivery details
    - tax_code_id: character field for tax code ID
    - freight_tax_code: character field for freight tax code

    Methods:
    - __str__(): Returns string representation of the Customer username
    """

    display_id = models.CharField(max_length=255, null=True, blank=True)
    myob_uid = models.CharField(unique=True, max_length=50, null=True, blank=True)
    myob_row_version = models.BigIntegerField(null=True, blank=True)
    uri = models.URLField(null=True, blank=True)

    name = models.CharField(max_length=255, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    is_individual = models.BooleanField(default=False)
    company_name = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    tax_code_fk = models.ForeignKey(TaxCode, on_delete=models.CASCADE, null=True, blank=True, related_name="customer_tax_code")
    freight_tax_code_fk = models.ForeignKey(TaxCode, on_delete=models.CASCADE, null=True, blank=True, related_name="customer_freight_tax_code")
    tax_code_id = models.CharField(max_length=100, null=True, blank=True)
    freight_tax_code = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            last_slip = Customer.objects.order_by("-pk").first()
            last_display_id = int(last_slip.pk) if last_slip else 0
            self.display_id = f"C{last_display_id + 1:07d}"

        super().save(*args, **kwargs)

    def update_myob_values(self, uid, row_version, uri):
        self.myob_uid = uid
        self.myob_row_version = row_version
        self.uri = uri
        self.save()

    def __str__(self):
        return f"{self.name}"

