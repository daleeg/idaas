# -*- coding: utf-8 -*-

import os
import uuid
import random
import sys
import shutil
import io
import chardet
import logging
import hashlib

from django.conf import settings
from django.utils import timezone

from django.core.files.uploadedfile import UploadedFile
import pandora.utils.constants as cst
from pandora.core.exceptions import EmptyDataError, FileEncodeError
from pandora.core.code import SUCCESS
from pandora.utils.base64utils import base64_to_jpg, base64_to_file
from pandora.utils.lru import lru_cache
from pandora.utils.image import resize_image, auto_rotate_image
LOG = logging.getLogger(__name__)
HORIZON_WHEN = "D"


def remove_file(_file):
    try:
        LOG.info("remove file :{}".format(_file))
        os.remove(_file)
    except Exception as e:
        LOG.error("Error: remove file {}, details:{}".format(_file, e))


@lru_cache(None)
def get_version_from_file():
    version = {
        "inside_version": "",
        "detail_version": "",
        "release_version": "",
    }
    version_file = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "classboard-version")
    try:
        with open(version_file, "r") as f:
            line = f.readline()
            try:
                version["inside_version"], version["detail_version"], version["release_version"] = line.split()
            except Exception as e:
                LOG.error("Error: parse version file {}, details:{}".format(version_file, e))

    except Exception as e:
        LOG.error("Error: get version file {}, details:{}".format(version_file, e))
    return version


def common_make_folder(path, mode=0o644):
    if not os.path.exists(path):
        try:
            os.makedirs(path, mode)
        except Exception as e:
            LOG.error("Error: makedirs {}, details:{}".format(path, e))
            return False
    return True


def remove_folder(_path):
    try:
        LOG.info("remove folder :{}".format(_path))
        shutil.rmtree(_path, ignore_errors=True)
    except Exception as e:
        LOG.error("Error: remove folder {}, details:{}".format(_path, e))


def gen_inner_path(trunk_file, prefix, content_type=None, when="N", md5=True):
    if not content_type:
        try:
            content_type = trunk_file.content_type.lower()
        except:
            content_type = "image/jpeg"

    if prefix:
        if "screenshot" in prefix:
            when = "N"
            md5 = False

        if "fix" in prefix:
            when = "N"
            md5 = False

        if "image" in prefix:
            when = "D"
            md5 = False
            content_type = ""
        inner_path = prefix.lower()
    else:
        inner_path = ""

    if when == "M":
        inner_path = os.path.join(inner_path, timezone.now().strftime("%Y%m"))
    elif when == "D":
        inner_path = os.path.join(inner_path, timezone.now().strftime("%Y%m/d%d"))
    elif when == "Y":
        inner_path = os.path.join(inner_path, timezone.now().strftime("%Y"))

    if content_type:
        inner_path = os.path.join(inner_path, content_type)

    if md5:
        md5_hash = get_md5_hash(trunk_file)
        if md5_hash:
            inner_path = os.path.join(md5_hash[0], inner_path)
    return inner_path


def save_trunk_file(trunk_file, prefix, name, content_type=None, when=HORIZON_WHEN, md5=False, is_shrink=True):
    # if trunk_file.size > cst.max_image_size:
    #     msg = "max image size {} real size: {}".format(cst.max_image_size, trunk_file.size)
    #     LOG.error(msg)
    #     return FILE_TOO_LARGE, msg
    inner_path = gen_inner_path(trunk_file, prefix, content_type, when, md5)
    file_root = os.path.join(settings.FILE_ROOT, inner_path)
    common_make_folder(file_root)
    if not isinstance(trunk_file, UploadedFile):
        file_name = "{}{}".format(name, ".jpg")
        fpath = base64_to_jpg(trunk_file, file_root, file_name)
        is_shrink = False
    else:
        ext = os.path.splitext(trunk_file.name)[1].lower()
        file_name = "{}{}".format(name, ext) if name else "{}{}".format(uuid.uuid4(), ext)
        fpath = os.path.join(file_root, file_name)
        with open(fpath, "wb") as f:
            for c in trunk_file.chunks(10240):
                f.write(c)
        auto_rotate_image(fpath)

    fmd5 = fpath + ".md5"
    with open(fpath, "rb") as rf:
        md5_hash = get_md5_hash(rf)
        with open(fmd5, "w") as f:
            f.write(md5_hash)

    if is_shrink:
        shrink = fpath + cst.SHRINK_SUFFIX
        try:
            resize_image(fpath, shrink)
        except:
            pass

    LOG.info(fpath)
    url_path = os.path.join(settings.FILE_URL, inner_path, file_name)
    url_path = url_path.replace("\\", "/")
    get_url_path_md5.cache_delete(url_path)
    return SUCCESS, url_path


def save_tmp_trunk_file(trunk_file, prefix, name, is_shrink=True):
    prefix = prefix.lower()
    unique = str(uuid.uuid4())
    file_root = os.path.join(settings.FILE_ROOT, "tmp", prefix, unique)
    common_make_folder(file_root)
    ext = os.path.splitext(trunk_file.name)[1]
    file_name = "{}{}".format(name, ext)
    fpath = os.path.join(file_root, file_name)
    LOG.info("save file: {}".format(fpath))
    with open(fpath, "wb") as f:
        for c in trunk_file.chunks(10240):
            f.write(c)
    auto_rotate_image(fpath)

    shrink = None
    if is_shrink:
        shrink = fpath + cst.SHRINK_SUFFIX
        try:
            resize_image(fpath, shrink)
        except:
            pass

    url_path = os.path.join(settings.FILE_URL, "tmp", prefix, unique, file_name)
    url_path = url_path.replace("\\", "/")
    get_url_path_md5.cache_delete(url_path)
    return fpath, url_path, shrink


def create_trunk_file_from_tmp(trunk_file, prefix, name, tmp_path, content_type=None, when=HORIZON_WHEN, md5=False,
                               is_shrink=True):
    inner_path = gen_inner_path(trunk_file, prefix, content_type, when, md5)
    file_root = os.path.join(settings.FILE_ROOT, inner_path, name)
    common_make_folder(file_root)
    ext = os.path.splitext(trunk_file.name)[1]

    file_name = "{}{}".format(str(uuid.uuid4())[0:8], ext)
    fpath = os.path.join(file_root, file_name)

    try:
        shutil.move(tmp_path, fpath)
        if is_shrink:
            shutil.move(tmp_path + cst.SHRINK_SUFFIX, fpath + cst.SHRINK_SUFFIX)
        LOG.info("mv file: from {} to {}".format(tmp_path, fpath))
    except Exception as e:
        LOG.error(e)
    finally:
        remove_folder(os.path.dirname(tmp_path))

    fmd5 = fpath + ".md5"
    with open(fpath, "rb") as rf:
        md5_hash = get_md5_hash(rf)
        with open(fmd5, "w") as f:
            f.write(md5_hash)

    url_path = os.path.join(settings.FILE_URL, inner_path, name, file_name)
    url_path = url_path.replace("\\", "/")
    LOG.info("static path: {}".format(url_path))
    get_url_path_md5.cache_delete(url_path)
    return url_path


def save_base64_file(trunk_file, prefix, name, content_type="jpeg", when=HORIZON_WHEN, md5=False, is_shrink=True):
    inner_path = gen_inner_path(trunk_file, prefix, content_type, when, md5)
    file_root = os.path.join(settings.FILE_ROOT.rstrip("/"), inner_path)
    common_make_folder(file_root)
    ext = cst.ext_map.get(content_type.upper(), ".tmp")
    file_name = "{}{}".format(name, ext) if name else "{}{}".format(uuid.uuid4(), ext)
    fpath = base64_to_file(trunk_file, file_root, file_name)
    auto_rotate_image(fpath)
    fmd5 = fpath + ".md5"
    with open(fpath, "rb") as rf:
        md5_hash = get_md5_hash(rf)
        with open(fmd5, "w") as f:
            f.write(md5_hash)
    if is_shrink:
        shrink = fpath + cst.SHRINK_SUFFIX
        try:
            resize_image(fpath, shrink)
        except:
            pass
    LOG.info(fpath)
    url_path = os.path.join(settings.FILE_URL.rstrip("/"), inner_path, file_name)
    url_path = url_path.replace("\\", "/")
    get_url_path_md5.cache_delete(url_path)
    return SUCCESS, url_path


@lru_cache(maxsize=None)
def get_path_url(path_name):
    url_path = os.path.join(settings.FILE_URL.rstrip("/"), path_name)
    url_path = url_path.replace("\\", "/")
    return url_path


@lru_cache(maxsize=None)
def url_2_file_path(url_path):
    return url_2_file_path_direct(url_path)


def url_2_file_path_direct(url_path):
    url_pre_len = len(settings.FILE_URL.rstrip("/")) + 1
    file_path = os.path.join(settings.FILE_ROOT.rstrip("/"), url_path[url_pre_len:])
    if sys.platform == "win32":
        file_path = file_path.replace("/", "\\")
    else:
        file_path = file_path.replace("\\", "/")

    return file_path


@lru_cache(maxsize=None)
def get_url_path_md5(url_path):
    if not url_path:
        return ""
    file_path = url_2_file_path(url_path)
    file_path_md5 = "{}.md5".format(file_path)
    try:
        if os.path.exists(file_path_md5) and random.randint(0, 9) < 9:
            with open(file_path_md5, "r") as f:
                md5_hash = f.read()
            return md5_hash
        else:
            with open(file_path, "rb") as f:
                md5_hash = get_md5_hash(f)
            with open(file_path_md5, "w") as f:
                f.write(md5_hash)
            return md5_hash

    except Exception as e:
        LOG.error(e)
    return ""


def get_md5_hash(instance):
    if isinstance(instance, str):
        md5_hash = hashlib.md5(instance.encode(encoding="utf8")).hexdigest()
        # LOG.info("str--{}".format(md5_hash))
    elif isinstance(instance, bytes):
        md5_hash = hashlib.md5(instance).hexdigest()
        # LOG.info("bytes--{}".format(md5_hash))
    else:
        md5_hash = hashlib.md5(instance.read()).hexdigest()
        # LOG.info("{}--{}".format(type(instance), md5_hash))
    return md5_hash


def read_csv(body):
    fp = io.BytesIO()
    for i in body.chunks():
        fp.write(i)
    data = fp.getvalue()
    lines = data.splitlines()
    if len(lines) < 2:
        raise EmptyDataError
    encode = chardet.detect(lines[0])
    data_encode = encode["encoding"] or ""
    if data_encode.upper() in ["UTF-8", "UTF-8-SIG"]:
        data_decode = data.decode(encode["encoding"], errors="ignore")
    elif data_encode.upper() in ["ISO-8859-5", "TIS-620", "GB2312"]:
        data_decode = data.decode("GBK", errors="ignore")
    else:
        raise FileEncodeError

    return data_decode


def parse_name_ext(file_name):
    """根据文件路径解析文件名与后缀"""
    (file_path, temp_file_name) = os.path.split(file_name)
    (shot_name, extension) = os.path.splitext(temp_file_name)
    extension = extension.replace(".", "") if extension else None
    return shot_name, extension


def parse_pid_file():
    file = settings.PID_FILE_PATH
    pid = mac = ""
    try:
        with open(file, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if "PID" in line:
                    pid = line.split("=")[1].strip()
                elif "MAC" in line:
                    mac = line.split("=")[1].strip()
    except:
        LOG.error("can not read pid file.")
    return pid, mac
