# Itachi Userbot - A telegram userbot.
# Copyright (C) 2021 Itachisann

# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY
# without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see < https: // www.gnu.org/licenses/>.


import configparser
import os
from distutils.util import strtobool

sample_config_file = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'sample_config.ini'
)


def resolve_env(config: configparser.ConfigParser):
    api_id = os.getenv('api_id', None)
    api_hash = os.getenv('api_hash', None)

    if "telethon" in config.sections() and not api_id and not api_hash:
        api_id = config['telethon'].get('api_id', False)
        api_hash = config['telethon'].get('api_hash', False)

    if not api_id or not api_hash:
        raise ValueError('You need to set your API Keys at least.')

    sample_config = configparser.ConfigParser()
    sample_config.read(sample_config_file)
    for section in sample_config.sections():
        if section not in config:
            config[section] = {}

    config['telethon']['api_id'] = api_id
    config['telethon']['api_hash'] = api_hash
    userbot = {
        'userbot_regexninja': strtobool(
            os.getenv('userbot_regexninja', 'False')
        ),
        'self_destruct_msg': strtobool(
            os.getenv('self_destruct_msg', 'True')
        ),
        'pm_permit': strtobool(os.getenv('pm_permit', 'False')),
        'console_logger_level': os.getenv('console_logger_level', None),
        'logger_group_id': int(os.getenv('logger_group_id', 0)),
        'userbot_prefix': os.getenv('userbot_prefix', None),
        'default_sticker_pack': os.getenv('default_sticker_pack', None),
        'default_animated_sticker_pack': os.getenv(
            'default_animated_sticker_pack', None
        )
    }

    plugins = {
        'repos': os.getenv(
            'repos', None
        ),
        'user': os.getenv(
            'user', None
        ),
        'token': os.getenv(
            'token', None
        )
    }

    make_config(config, 'userbot', userbot)
    make_config(config, 'plugins', plugins)


def make_config(
    config: configparser.ConfigParser,
    section: str, section_dict: dict
) -> None:
    UNACCETPABLE = ['', '0', 'None', 'none', 0, None]
    for key, value in section_dict.items():
        if value is not None and value not in UNACCETPABLE:
            config[section][key] = str(value)
