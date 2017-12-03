from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin)
# Create your models here.


# 创建objects对象的类
class UserProfileManager(BaseUserManager):
    def create_user(self, email, date_of_birth, password=None):
        """        Creates and saves a User with the given email, date of        birth and password.        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, date_of_birth, password):
        """        Creates and saves a superuser with the given email, date of        birth and password.        """
        user = self.create_user(
            email,
            password=password,
            date_of_birth=date_of_birth,
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# 用户验证模型
class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    bind_hosts = models.ManyToManyField('BindHost', blank=True)
    host_groups = models.ManyToManyField("HostGroup", blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'                # 指定用户名字段
    REQUIRED_FIELDS = ['date_of_birth']     # 设置必填字段

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class IDC(models.Model):
    """IDC机房"""
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Host(models.Model):
    """主机"""
    host_name = models.CharField(max_length=256)
    ip_addr = models.GenericIPAddressField(unique=True)
    idc = models.ForeignKey(to="IDC", on_delete=models.PROTECT)

    def __str__(self):
        return self.host_name


class HostUser(models.Model):
    """主机用户"""
    username = models.CharField(max_length=128)
    auth_type_choices = ((0, 'Password'),
                         (1, 'KEY'))
    auth_type = models.PositiveSmallIntegerField(choices=auth_type_choices)
    password = models.CharField(max_length=256)

    class Meta:
        unique_together = ('username', 'auth_type', 'password')

    def __str__(self):
        return "<username:%s,auth_type:%s,password:%s>" % (self.username, self.get_auth_type_display(), self.password)


class BindHost(models.Model):
    """主机用户与主机绑定"""
    host = models.ForeignKey("Host", on_delete=models.PROTECT)
    user = models.ForeignKey("HostUser", on_delete=models.PROTECT)

    class Meta:
        unique_together = ('host', 'user')

    def __str__(self):
        return "<host:%s,user:%s>" % (self.host, self.user)


class HostGroup(models.Model):
    """绑定主机分组"""
    name = models.CharField(max_length=64, unique=True)
    bind_hosts = models.ManyToManyField('BindHost')

    def __str__(self):
        return self.name


class SessionLog(models.Model):
    """ssh 记录"""
    user = models.ForeignKey("UserProfile", on_delete=models.PROTECT)
    bind_host = models.ForeignKey("BindHost", on_delete=models.PROTECT)
    # log_file = models.FilePathField()
    date = models.DateTimeField(auto_now_add=True)
    session_tag = models.CharField(max_length=128)

    def __str__(self):
        return "<user:%s,bind_host:%s,session_tag:%s>" % (self.user, self.bind_host, self.session_tag)
