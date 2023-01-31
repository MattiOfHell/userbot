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


import io

import PIL
from telethon import errors
from telethon.tl import functions, types
from telethon.utils import get_peer_id
from userbot import LOGGER, client
from userbot.core.events import NewMessage
from userbot.plugins.functions.parser import Parser

plugin_category = "user"


@client.createCommand(
    command=("info [Utente]", plugin_category),
    outgoing=True, regex=r"info(?: |$|\n)([\s\S]*)"
)
async def info(event: NewMessage.Event) -> None:
    match = event.matches[0].group(1)
    entities = []
    if match:
        entities, _ = await client.parse_arguments(match)
        if "this" in entities:
            entities.remove("this")
            entities.append(event.chat_id)
    elif event.reply_to_msg_id:
        if not entities:
            reply = await event.get_reply_message()
            user = reply.sender_id
            if reply.fwd_from:
                if reply.fwd_from.from_id:
                    user = reply.fwd_from.from_id
            entities.append(user)
    else:
        entities.append("self")
    users = ""
    chats = ""
    channels = ""
    failed = []
    for user in entities:
        try:
            input_entity = await client.get_input_entity(user)
            if isinstance(input_entity, types.InputPeerChat):
                full_chat = await client(
                    functions.messages.GetFullChatRequest(input_entity)
                )
                string = await Parser.parse_full_chat(full_chat, event)
                chats += f"\n{chats}\n"
            elif isinstance(input_entity, types.InputPeerChannel):
                full_channel = await client(
                    functions.channels.GetFullChannelRequest(input_entity)
                )
                string = await Parser.parse_full_chat(full_channel, event)
                channels += f"\n{string}\n"
            else:
                full_user = await client(
                    functions.users.GetFullUserRequest(input_entity)
                )
                string = await Parser.parse_full_user(full_user, event)
                users += f"\n{string}\n"
        except Exception as e:
            LOGGER.debug(e)
            failed.append(user)

    if users:
        photo = full_user.profile_photo
        if photo:
            await event.delete()
            await client.send_message(event.chat_id, "<b>⚙️ INFO UTENTE ⚙️ </b>" + users, file=photo, parse_mode='html')
        else:
            await event.answer("<b>⚙️ INFO UTENTE ⚙️ </b>" + users, parse_mode='html')
    if chats:
        await event.answer("<b>⚙️ INFO GRUPPO ⚙️</b>" + chats, parse_mode='html')
    if channels:
        await event.answer("<b>⚙️ INFO CHAT ⚙️</b>" + channels, parse_mode='html')

    if failed:
        failedtext = "**Impossibile trovare:**\n"
        failedtext += ", ".join(f'`{u}`' for u in failed)
        await event.answer(failedtext)
    elif not (users or chats or channels):
        await event.answer("**Impossibile trovare:**", self_destruct=2)


@client.createCommand(
    command=("bio [Bio]", plugin_category),
    outgoing=True, regex="bio(?: |$)(.*)$"
)
async def bio(event: NewMessage.Event) -> None:
    match = event.matches[0].group(1)
    about = (await client(functions.users.GetFullUserRequest("self"))).about
    if not match:
        if about:
            await event.answer(f"**📕 Bio:\n {about}**")
        else:
            await event.answer("`Attualmente non hai bio.`")
        return

    try:
        await client(functions.account.UpdateProfileRequest(about=match))
        await event.answer(
            f"`✅ Bio cambiata in {match}.`",
            log=("bio", f"Bio cambiata da {about} a{match}")
        )
    except errors.AboutTooLongError:
        await event.answer("`La bio che vuoi impostare è troppo lunga.`")


@client.createCommand(
    command=("username [Username]", plugin_category),
    outgoing=True, regex="username(?: |$)(.*)$"
)
async def username(event: NewMessage.Event) -> None:
    match = event.matches[0].group(1)
    u1 = (await client.get_me()).username
    if not match:
        if u1:
            await event.answer(f"👤 Utente: **@{u1}**")
        else:
            await event.answer("`Attualmente non hai username.`")
        return

    try:
        await client(functions.account.UpdateUsernameRequest(username=match))
        await event.answer(
            f"**✅ Hai cambiato il tuo username in @{match}**",
            log=("username", f"Username cambiato da @{u1} a @{match}")
        )
    except errors.UsernameOccupiedError:
        await event.answer("`Questo username è già in uso.`")
    except errors.UsernameNotModifiedError:
        await event.answer("`Username non modificato.`")
    except errors.UsernameInvalidError:
        await event.answer("`Username non modificato.`")


@client.createCommand(
    command=("on", plugin_category),
    outgoing=True, regex="on(?: |$)(.*)$"
)
async def on(event: NewMessage.Event) -> None:
    string = '[Online] '
    me = await client.get_me()
    if string not in me.first_name:
        new_name = string + me.first_name
    else:
        new_name = me.first_name
    if '[Offline] ' in me.first_name:
        v = me.first_name
        new_name = v.replace('[Offline] ', string)

    try:
        await client(functions.account.UpdateProfileRequest(
            first_name=new_name
        ))
        await event.answer("__Sei andato online!__", self_destruct=2)
    except errors.FirstNameInvalidError:
        await event.answer("`Nome invalido`")
    except Exception as e:
        await event.answer(f'```{await client.get_traceback(e)}```')


@client.createCommand(
    command=("off", plugin_category),
    outgoing=True, regex="off(?: |$)(.*)$"
)
async def off(event: NewMessage.Event) -> None:
    string = '[Offline] '
    me = await client.get_me()
    if '[Online] ' in me.first_name:
        v = me.first_name
        new_name = v.replace('[Online] ', string)
        try:
            await client(functions.account.UpdateProfileRequest(
                first_name=new_name
            ))
            await event.answer("__Sei andato offline!__", self_destruct=2)
        except errors.FirstNameInvalidError:
            await event.answer("`Nome invalido`")
        except Exception as e:
            await event.answer(f'```{await client.get_traceback(e)}```')


@client.createCommand(
    command=("pfp", plugin_category),
    outgoing=True, regex="pfp$"
)
async def pfp(event: NewMessage.Event) -> None:
    reply = await event.get_reply_message()
    if not reply:
        photo = await client(functions.users.GetFullUserRequest("self"))
        photo = photo.profile_photo
        if photo:
            await event.delete()
            await event.answer(file=photo)
        else:
            await event.answer("`Attualmente non hai foto profilo.`")
        return

    if (
        (reply.document and reply.document.mime_type.startswith("image")) or
        reply.photo or reply.sticker
    ):
        if reply.sticker and not reply.sticker.mime_type == "image/webp":
            await event.answer("`Sticker invalido.`")
            return
        try:
            temp_file = io.BytesIO()
            await client.download_media(reply, temp_file)
        except Exception as e:
            await event.answer(
                f'```{await client.get_traceback(e)}```',
                reply=True
            )
            temp_file.close()
            return
        temp_file.seek(0)
        if reply.sticker:
            sticker = io.BytesIO()
            pilImg = PIL.Image.open(temp_file)
            pilImg.save(sticker, format="PNG")
            pilImg.close()
            sticker.seek(0)
            sticker.name = "sticcer.png"
            photo = await client.upload_file(sticker)
            temp_file.close()
            sticker.close()
        else:
            photo = await client.upload_file(temp_file)
            temp_file.close()
    else:
        await event.answer("`Media invalido.`")
        return

    try:
        await client(functions.photos.UploadProfilePhotoRequest(photo))
        await event.answer(
            "`✅ La tua foto profilo è stata cambiata con successo.`",
            log=("pfp", "Changed profile picture")
        )
    except errors.FilePartsInvalidError:
        await event.answer("`Il numero di file è invalido.`")
    except errors.ImageProcessFailedError:
        await event.answer("`Errore nel processare l'immagine`")
    except errors.PhotoCropSizeSmallError:
        await event.answer("`Foto troppo piccola`")
    except errors.PhotoExtInvalidError:
        await event.answer("`Questa foto non è supportata.`")


@client.createCommand(
    command=("id [Utente]", plugin_category),
    outgoing=True, regex=r"id(?: |$|\n)([\s\S]*)"
)
async def whichid(event: NewMessage.Event) -> None:
    match = event.matches[0].group(1)
    text = ""
    if not match and not event.reply_to_msg_id:
        attr = "first_name" if event.is_private else "title"
        text = f"🆔 {getattr(event.chat, attr)}: "
        text += f"`{get_peer_id(event.chat_id)}`"
    elif event.reply_to_msg_id:
        reply = await event.get_reply_message()
        user = reply.sender_id
        if reply.fwd_from:
            if reply.fwd_from.from_id:
                user = reply.fwd_from.from_id
        peer = get_peer_id(user)
        text = f"🆔 [{peer}](tg://user?id={peer}): `{peer}`"
    else:
        failed = []
        strings = []
        users, _ = await client.parse_arguments(match)
        for user in users:
            try:
                entity = await client.get_input_entity(user)
                peer = get_peer_id(entity)
                if isinstance(entity, types.InputPeerChat):
                    chat = await client(
                        functions.messages.GetFullChatRequest(entity)
                    )
                    strings.append(
                        f"🆔 [{chat.chats[0].title}](tg://resolve?domain={peer}): `{peer}`"
                    )
                elif isinstance(entity, types.InputPeerChannel):
                    channel = await client(
                        functions.channels.GetFullChannelRequest(entity)
                    )
                    strings.append(
                        f"🆔 [{channel.chats[0].title}](tg://resolve?domain={peer}): `{peer}`"
                    )
                else:
                    user = await client(
                        functions.users.GetFullUserRequest(entity)
                    )
                    strings.append(
                        f"🆔 [@{user.user.username}](tg://user?id={peer}): `{peer}`"
                    )
            except Exception as e:
                failed.append(user)
                LOGGER.debug(e)
        if strings:
            text = "\n".join(strings)
        if failed:
            ftext = "**Utenti non trovati:**\n"
            ftext += ", ".join(f'`{f}`' for f in failed)
            await event.answer(ftext, reply=True)
    if text:
        await event.answer(text)
