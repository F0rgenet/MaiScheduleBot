import re
from sqlalchemy.exc import NoResultFound
from xmltodict import parse as xml_parse
from loguru import logger

from pathlib import Path
from ..models import Group, Subject
from .. import Database

