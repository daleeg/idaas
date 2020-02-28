# Generated by Django 3.0.3 on 2020-02-28 00:33

import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import pandora.models.account.user
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('uid', models.UUIDField(db_index=True, default=uuid.uuid4, help_text='唯一标识uid', primary_key=True, serialize=False)),
                ('is_deleted', models.DateTimeField(default=False, help_text='表项的删除时间，为空标识未删除', null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, help_text='创建时间, 2018-1-1T1:1:1.1111')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改时间, 2018-1-1T1:1:1.1111')),
                ('name', models.CharField(help_text='名称,str(64)', max_length=64)),
                ('description', models.TextField(blank=True, help_text='简介', null=True)),
                ('phone', models.CharField(blank=True, help_text='官方电话, str(20)', max_length=20, null=True)),
                ('code', models.CharField(blank=True, help_text='学校唯一标识码, str(64)', max_length=64, null=True)),
                ('province', models.CharField(help_text='省, str(20)', max_length=20)),
                ('city', models.CharField(help_text='市, str(20)', max_length=20)),
                ('area', models.CharField(help_text='区, str(20)', max_length=20)),
                ('avatar', models.CharField(blank=True, help_text='校徽图片访问URL, str(256)', max_length=256, null=True)),
                ('motto', models.CharField(blank=True, help_text='校训, str(256)', max_length=256, null=True)),
                ('principal_name', models.CharField(blank=True, help_text='学校责任人姓名, str(64)', max_length=64, null=True)),
                ('principal_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='学校责任人邮箱')),
                ('principal_phone', models.CharField(blank=True, help_text='学校责任人电话, str(20)', max_length=20, null=True)),
                ('specific', models.TextField(blank=True, help_text='个性化信息', null=True)),
                ('brief_img', models.CharField(blank=True, help_text='简介图片路径', max_length=256, null=True)),
                ('face_group', models.CharField(blank=True, help_text='人脸组', max_length=128, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('uid', models.UUIDField(db_index=True, default=uuid.uuid4, help_text='唯一标识uid', primary_key=True, serialize=False)),
                ('is_deleted', models.DateTimeField(default=False, help_text='表项的删除时间，为空标识未删除', null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, help_text='创建时间, 2018-1-1T1:1:1.1111')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改时间, 2018-1-1T1:1:1.1111')),
                ('specific', models.CharField(blank=True, help_text='个性化信息, str(2048)', max_length=2048, null=True)),
                ('avatar', models.CharField(blank=True, help_text='图片访问URL, str(256)', max_length=256, null=True)),
                ('extra_info', models.TextField(blank=True, help_text='额外信息', null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('school', models.ForeignKey(blank=True, help_text='学校', null=True, on_delete=django.db.models.deletion.SET_NULL, to='pandora.School')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', pandora.models.account.user.UserManager()),
            ],
        ),
    ]
