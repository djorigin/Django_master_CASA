# PROPOSED CERTIFICATE ARCHITECTURE FIX
# File: accounts/models.py - Additional models to add


class CertificateType(models.Model):
    """
    Master certificate types for aviation compliance
    """

    CATEGORY_CHOICES = [
        ('pilot', 'Pilot Certificates'),
        ('staff', 'Staff Certificates'),
        ('maintenance', 'Maintenance Certificates'),
        ('safety', 'Safety Certificates'),
        ('training', 'Training Certificates'),
    ]

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    validity_period_months = models.IntegerField(
        help_text="Certificate validity in months (0 = permanent)"
    )
    required_training = models.ManyToManyField(
        'core.TrainingSyllabus',
        blank=True,
        help_text="Training required to obtain this certificate",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Certificate Type"
        verbose_name_plural = "Certificate Types"
        ordering = ['category', 'code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class PersonalCertificate(models.Model):
    """
    Individual certificates held by pilots and staff
    """

    STATUS_CHOICES = [
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked'),
        ('pending', 'Pending Approval'),
    ]

    # Link to person (pilot or staff)
    pilot = models.ForeignKey(
        'PilotProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='certificates',
    )
    staff = models.ForeignKey(
        'StaffProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='certificates',
    )

    certificate_type = models.ForeignKey(CertificateType, on_delete=models.PROTECT)
    certificate_number = models.CharField(max_length=50)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='valid')

    # Issuing Authority
    issuing_authority = models.CharField(max_length=100)
    issuing_officer = models.CharField(max_length=100, blank=True)

    # Supporting Documentation
    certificate_document = models.FileField(
        upload_to='certificates/%Y/%m/', blank=True, null=True
    )

    # Training Link
    related_training = models.ForeignKey(
        'core.TrainingRegister',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Training record that led to this certificate",
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Personal Certificate"
        verbose_name_plural = "Personal Certificates"
        unique_together = [
            ['pilot', 'certificate_type', 'certificate_number'],
            ['staff', 'certificate_type', 'certificate_number'],
        ]
        ordering = ['-issue_date']

    def clean(self):
        # Ensure only one of pilot or staff is set
        if self.pilot and self.staff:
            raise ValidationError("Certificate cannot belong to both pilot and staff")
        if not self.pilot and not self.staff:
            raise ValidationError("Certificate must belong to either pilot or staff")

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    @property
    def days_until_expiry(self):
        if self.expiry_date:
            return (self.expiry_date - timezone.now().date()).days
        return None

    @property
    def holder(self):
        return self.pilot or self.staff

    def __str__(self):
        holder = (
            self.pilot.user.get_full_name()
            if self.pilot
            else self.staff.user.get_full_name()
        )
        return f"{holder} - {self.certificate_type.code}"
