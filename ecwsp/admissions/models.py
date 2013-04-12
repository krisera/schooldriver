from django.contrib.localflavor.us.models import *
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.db.models.signals import m2m_changed
from custom_field.custom_field import CustomFieldModel
from ecwsp.sis.models import get_default_language, GradeLevel

import datetime

if not 'ecwsp.standard_test' in settings.INSTALLED_APPS:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured('admissions requires standard_test please add ecwsp.standard_test to INSTALLED_APPS')

class AdmissionLevel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    order = models.IntegerField(unique=True, help_text="Order in which level appears. 1 being first.")
    def __unicode__(self):
        return unicode(self.name)
    def edit(self):
        return "Edit"
    def show_checks(self):
        """Show checks needed for this level"""
        msg = '|'
        for check in self.admissioncheck_set.all():
            msg += "%s | " % (check.name,)
        return msg
    class Meta:
        ordering = ('order',)
        
    
class AdmissionCheck(models.Model):
    name = models.CharField(max_length=255)
    level = models.ForeignKey(AdmissionLevel)
    required = models.BooleanField(
        default=True,
        help_text="When true, applicant cannot meet any level beyond this. When false, "\
                  "applicant can leapfrog check items.")
    class Meta:
        ordering = ('level','name')
    def __unicode__(self):
        return unicode(self.name)

class EthnicityChoice(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        ordering = ['name']
        
class ReligionChoice(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        ordering = ['name']

class HeardAboutUsOption(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        ordering = ['name']
    
class FirstContactOption(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        ordering = ['name']

class ApplicationDecisionOption(models.Model):
    name = models.CharField(max_length=255, unique=True)
    level = models.ManyToManyField(
        AdmissionLevel,
        blank=True,
        null=True,
        help_text="This decision can apply for these levels.")
    def __unicode__(self):
        return unicode(self.name)

class BoroughOption(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        ordering = ['name']

class SchoolType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __unicode__(self):
        return unicode(self.name)

class PlaceOfWorship(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __unicode__(self):
        return unicode(self.name)

class FeederSchool(models.Model):
    name = models.CharField(max_length=255)
    school_type = models.ForeignKey(SchoolType, blank=True, null=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        ordering = ['name']
        
class OpenHouse(models.Model):
    name = models.CharField(max_length=255, blank=True)
    date = models.DateField(blank=True, null=True, validators=settings.DATE_VALIDATORS)
    def __unicode__(self):
        return unicode(self.name) + " " + unicode(self.date)
    class Meta:
        ordering = ('-date',)

class WithdrawnChoices(models.Model):
    name = models.CharField(max_length=500)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Withdrawn Choices"
        
class CountryOption(models.Model):
    name = models.CharField(max_length=500)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        ordering = ['name']
        
class ImmigrationOption(models.Model):
    name = models.CharField(max_length=500)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        ordering = ['name']
 

def get_default_country():
    return CountryOption.objects.get_or_create(name=settings.ADMISSIONS_DEFAULT_COUNTRY)[0]
def get_school_year():
    try:
        return SchoolYear.objects.get(active_year=True).get_next_by_end_date()
    except:
        return None
def get_year():
    if GradeLevel.objects.count():
        return GradeLevel.objects.all()[0]
class Applicant(models.Model, CustomFieldModel):
    fname = models.CharField(max_length=255, verbose_name="First Name")
    mname = models.CharField(max_length=255, verbose_name="Middle Name", blank=True)
    lname = models.CharField(max_length=255, verbose_name="Last Name")
    pic = models.ImageField(upload_to="applicant_pics",blank=True, null=True)
    sex = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')), blank=True)
    bday = models.DateField(blank=True, null=True, verbose_name="Birth Date", validators=settings.DATE_VALIDATORS)
    unique_id = models.IntegerField(blank=True, null=True, unique=True)
    street = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=360, blank=True)
    state = USStateField(blank=True)
    zip = models.CharField(max_length=10, blank=True)
    #single_parent = models.BooleanField()
    #qualify_for_reduced_lunch = models.BooleanField()
    ssn = models.CharField(max_length=11, blank=True, verbose_name="SSN")
    parent_email = models.EmailField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True)
    family_preferred_language = models.ForeignKey(
        'sis.LanguageChoice',
        blank=True,
        null=True,
        default=get_default_language)
    siblings = models.ManyToManyField('sis.Student', blank=True)
    year = models.ForeignKey(
        'sis.GradeLevel',
        blank=True,
        null=True,
        help_text="Applying for this grade level",
        default=get_year)
    school_year = models.ForeignKey('sis.SchoolYear', blank=True, null=True, default=get_school_year)
    parent_guardians = models.ManyToManyField('sis.EmergencyContact', verbose_name="Student Contact", blank=True, null=True)
    ethnicity = models.ForeignKey(EthnicityChoice, blank=True, null=True)
    hs_grad_yr = models.IntegerField(blank=True, null=True, max_length=4)
    elem_grad_yr = models.IntegerField(blank=True, null=True, max_length=4)
    present_school = models.ForeignKey(FeederSchool, blank=True, null=True)
    present_school_typed = models.CharField(max_length=255, blank=True, help_text="This is intented for applicants apply for the school. Administrators should use the above.")
    present_school_type_typed = models.CharField(max_length=255, blank=True)
    religion = models.ForeignKey(ReligionChoice, blank=True, null=True)
    place_of_worship = models.ForeignKey(PlaceOfWorship, blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True, validators=settings.DATE_VALIDATORS)
    open_house_attended = models.ManyToManyField(OpenHouse, blank=True, null=True)
    parent_guardian_first_name = models.CharField(max_length=150, blank=True)
    parent_guardian_last_name = models.CharField(max_length=150, blank=True)
    relationship_to_student = models.CharField(max_length=500, blank=True)
    heard_about_us = models.ForeignKey(HeardAboutUsOption, blank=True, null=True)
    from_online_inquiry = models.BooleanField()
    first_contact = models.ForeignKey(FirstContactOption, blank=True, null=True)
    borough = models.ForeignKey(BoroughOption, blank=True, null=True)
    country_of_birth = models.ForeignKey(CountryOption, blank=True, null=True, default=get_default_country)
    immigration_status = models.ForeignKey(ImmigrationOption, blank=True, null=True)
    ready_for_export = models.BooleanField()
    sis_student = models.OneToOneField(
        'sis.Student',
        blank=True,
        null=True,
        related_name="appl_student",
        on_delete=models.SET_NULL)
    
    total_income = models.DecimalField(max_digits=10, decimal_places=2, blank=True,null=True)
    adjusted_available_income = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    calculated_payment = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    
    date_added = models.DateField(auto_now_add=True, blank=True, null=True, validators=settings.DATE_VALIDATORS)
    level = models.ForeignKey(AdmissionLevel, blank=True, null=True, on_delete=models.SET_NULL)
    checklist = models.ManyToManyField(AdmissionCheck, blank=True, null=True)
    application_decision = models.ForeignKey(ApplicationDecisionOption, blank=True, null=True)
    application_decision_by = models.ForeignKey(User, blank=True, null=True)
    withdrawn = models.ForeignKey(WithdrawnChoices, blank=True, null=True)
    withdrawn_note = models.CharField(max_length=500, blank=True)
    first_to_college = models.BooleanField(blank=True)
    individual_education_plan = models.BooleanField(blank=True)
    lives_with = models.CharField(
        blank=True,
        max_length=50,
        choices=(('Both Parents','Both Parents'),('Mother','Mother'),('Father','Father'),('Guardian(s)','Guardian(s)'),),
    )
    
    class Meta:
        ordering = ('lname','fname',)
    
    def __unicode__(self):
        return "%s %s %s" % (self.fname, self.mname, self.lname)
    
    def set_cache(self, contact):
        self.parent_guardian_first_name = contact.fname
        self.parent_guardian_last_name = contact.lname
        self.street = contact.street
        self.state = contact.state
        self.zip = contact.zip
        self.city = contact.city
        self.parent_email = contact.email
        self.save()
        
        for contact in self.parent_guardians.exclude(id=contact.id):
            # There should only be one primary contact!
            if contact.primary_contact:
                contact.primary_contact = False
                contact.save()
    
    def __set_level(self):
        prev = None
        for level in AdmissionLevel.objects.all():
            checks = level.admissioncheck_set.filter(required=True)
            i = 0
            for check in checks:
                if check in self.checklist.all():
                    i += 1
            if not i >= checks.count():
                break
            prev = level
        self.level = prev
    
    def save(self, *args, **kwargs):
        if self.id:
            self.__set_level()
        # create contact log entry on application decision
        if self.application_decision and self.id:
            old = Applicant.objects.get(id=self.id)
            if not old.application_decision:
                contact_log = ContactLog(
                    user = self.application_decision_by,
                    applicant = self,
                    note = "Application Decision: %s" % (self.application_decision,)
                )
                contact_log.save()
        super(Applicant, self).save(*args, **kwargs)
        
def cache_applicant_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    for ec in instance.parent_guardians.filter(primary_contact=True):
        ec.cache_student_addresses()

m2m_changed.connect(cache_applicant_m2m, sender=Applicant.parent_guardians.through)

class ContactLog(models.Model):
    applicant = models.ForeignKey(Applicant)
    date = models.DateField(validators=settings.DATE_VALIDATORS)
    user = models.ForeignKey(User, blank=True, null=True)
    note = models.TextField()
    
    def save(self, **kwargs):
        if not self.date and not self.id:
            self.date = datetime.date.today()
        super(ContactLog,self).save()
    
    def __unicode__(self):
        return "%s %s: %s" % (self.user, self.date, self.note)
    

class ApplicantStandardTestResult(models.Model):
    """ Standardized test instance. This is the results of a student taking a test """
    date = models.DateField(default=datetime.date.today(), validators=settings.DATE_VALIDATORS)
    applicant = models.ForeignKey(Applicant)
    test = models.ForeignKey('standard_test.StandardTest')
    show_on_reports = models.BooleanField(default=True, help_text="If true, show this test result on a report such as a transcript. " + \
        "Note entire test types can be marked as shown on report or not. This is useful if you have a test that is usually shown, but have a few instances where you don't want it to show.")
    
    class Meta:
        unique_together = ('date', 'applicant', 'test')
    
    def __unicode__(self):
        try:
            return '%s %s %s' % (unicode(self.applicant), unicode(self.test), self.date)
        except:
            return "Standard Test Result"
    
    @property
    def total(self):
        """Returns total for the test instance
        This may be calculated or marked as "is_total" on the category
        """
        if self.test.calculate_total:
            total = 0
            for cat in self.standardcategorygrade_set.all():
                total += cat.grade
            return str(total).rstrip('0').rstrip('.')
        elif self.standardcategorygrade_set.filter(category__is_total=True):
            totals = self.standardcategorygrade_set.filter(category__is_total=True)
            if totals:
                return str(totals[0].grade).rstrip('0').rstrip('.')
        else:
            return 'N/A'

class ApplicantStandardCategoryGrade(models.Model):
    """ Grade for a category and result """
    category = models.ForeignKey('standard_test.StandardCategory')
    result = models.ForeignKey(ApplicantStandardTestResult)
    grade = models.DecimalField(max_digits=6,decimal_places=2)
