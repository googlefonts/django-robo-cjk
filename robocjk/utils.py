from fontTools.pens.recordingPen import RecordingPointPen
from fontTools.ufoLib.glifLib import readGlyphFromString, writeGlyphToString


class GlyphObject:
    pass


def format_glif(s):
    glyph = GlyphObject()
    recorder = RecordingPointPen()
    readGlyphFromString(s, glyph, pointPen=recorder)
    return writeGlyphToString(glyph.name, glyph, drawPointsFunc=recorder.replay)


def char_to_unicode(s):
    return hex(ord(s))[2:].zfill(4).upper()


def unicodes_str_to_list(unicodes_str, to_int=False):
    if not unicodes_str:
        return []
    unicodes_list = unicodes_str.split(",")
    if to_int:
        unicodes_list = [int(unicode_hex_str, 16) for unicode_hex_str in unicodes_list]
    return unicodes_list


def unicode_to_char(s):
    s = s.lstrip("0").lower()
    if not s:
        return ""
    return chr(int(f"0x{s}", 16))


illegal_characters = '" * + / : < > ? [ \\ ] | \0'.split(" ")
illegal_characters += [chr(i) for i in range(1, 32)]
illegal_characters += [chr(0x7F)]
reserved_filenames = "CON PRN AUX CLOCK$ NUL A:-Z: COM1".lower().split(" ")
reserved_filenames += "LPT1 LPT2 LPT3 COM2 COM3 COM4".lower().split(" ")
filename_max_length = 255


def username_to_filename(username, existing=[], prefix="", suffix=""):
    """
    existing should be a case-insensitive list
    of all existing file names.

    >>> username_to_filename(u"a")
    u'a'
    >>> username_to_filename(u"A")
    u'A_'
    >>> username_to_filename(u"AE")
    u'A_E_'
    >>> username_to_filename(u"Ae")
    u'A_e'
    >>> username_to_filename(u"ae")
    u'ae'
    >>> username_to_filename(u"aE")
    u'aE_'
    >>> username_to_filename(u"a.alt")
    u'a.alt'
    >>> username_to_filename(u"A.alt")
    u'A_.alt'
    >>> username_to_filename(u"A.Alt")
    u'A_.A_lt'
    >>> username_to_filename(u"A.aLt")
    u'A_.aL_t'
    >>> username_to_filename(u"A.alT")
    u'A_.alT_'
    >>> username_to_filename(u"T_H")
    u'T__H_'
    >>> username_to_filename(u"T_h")
    u'T__h'
    >>> username_to_filename(u"t_h")
    u't_h'
    >>> username_to_filename(u"F_F_I")
    u'F__F__I_'
    >>> username_to_filename(u"f_f_i")
    u'f_f_i'
    >>> username_to_filename(u"Aacute_V.swash")
    u'A_acute_V_.swash'
    >>> username_to_filename(u".notdef")
    u'_notdef'
    >>> username_to_filename(u"con")
    u'_con'
    >>> username_to_filename(u"CON")
    u'C_O_N_'
    >>> username_to_filename(u"con.alt")
    u'_con.alt'
    >>> username_to_filename(u"alt.con")
    u'alt._con'
    """
    # the incoming name must be a unicode string
    # assert isinstance(username, unicode,
    #     "The value for username must be a unicode string.")
    # establish the prefix and suffix lengths
    prefix_length = len(prefix)
    suffix_length = len(suffix)
    # replace an initial period with an _
    # if no prefix is to be added
    if not prefix and username[0] == ".":
        username = "_" + username[1:]
    # filter the user name
    filtered_username = []
    for character in username:
        # replace illegal characters with _
        if character in illegal_characters:
            character = "_"
        # add _ to all non-lower characters
        elif character != character.lower():
            character += "_"
        filtered_username.append(character)
    username = "".join(filtered_username)
    # clip to 255
    slice_length = filename_max_length - prefix_length - suffix_length
    username = username[:slice_length]
    # test for illegal files names
    parts = []
    for part in username.split("."):
        if part.lower() in reserved_filenames:
            part = "_" + part
        parts.append(part)
    username = ".".join(parts)
    # test for clash
    fullname = prefix + username + suffix
    if fullname.lower() in existing:
        fullname = _handle_clash1(username, existing, prefix, suffix)
    # finished
    return fullname


def _handle_clash1(username, existing=[], prefix="", suffix=""):
    """
    existing should be a case-insensitive list
    of all existing file names.

    >>> prefix = ("0" * 5) + "."
    >>> suffix = "." + ("0" * 10)
    >>> existing = ["a" * 5]

    >>> e = list(existing)
    >>> _handle_clash1(username="A" * 5, existing=e,
    ...     prefix=prefix, suffix=suffix)
    '00000.AAAAA000000000000001.0000000000'

    >>> e = list(existing)
    >>> e.append(prefix + "aaaaa" + "1".zfill(15) + suffix)
    >>> _handle_clash1(username="A" * 5, existing=e,
    ...     prefix=prefix, suffix=suffix)
    '00000.AAAAA000000000000002.0000000000'

    >>> e = list(existing)
    >>> e.append(prefix + "AAAAA" + "2".zfill(15) + suffix)
    >>> _handle_clash1(username="A" * 5, existing=e,
    ...     prefix=prefix, suffix=suffix)
    '00000.AAAAA000000000000001.0000000000'
    """
    # if the prefix length + user name length + suffix length + 15 is at
    # or past the maximum length, silce 15 characters off of the user name
    prefix_length = len(prefix)
    suffix_length = len(suffix)
    if prefix_length + len(username) + suffix_length + 15 > filename_max_length:
        total_length = prefix_length + len(username) + suffix_length + 15
        slice_length = filename_max_length - total_length
        username = username[:slice_length]
    final_name = None
    # try to add numbers to create a unique name
    counter = 1
    while final_name is None:
        name = username + str(counter).zfill(15)
        fullname = prefix + name + suffix
        if fullname.lower() not in existing:
            final_name = fullname
            break
        else:
            counter += 1
        if counter >= 999999999999999:
            break
    # if there is a clash, go to the next fallback
    if final_name is None:
        final_name = _handle_clash2(existing, prefix, suffix)
    # finished
    return final_name


def _handle_clash2(existing=[], prefix="", suffix=""):
    """
    existing should be a case-insensitive list
    of all existing file names.

    >>> prefix = ("0" * 5) + "."
    >>> suffix = "." + ("0" * 10)
    >>> existing = [prefix + str(i) + suffix for i in range(100)]

    >>> e = list(existing)
    >>> _handle_clash2(existing=e, prefix=prefix, suffix=suffix)
    '00000.100.0000000000'

    >>> e = list(existing)
    >>> e.remove(prefix + "1" + suffix)
    >>> _handle_clash2(existing=e, prefix=prefix, suffix=suffix)
    '00000.1.0000000000'

    >>> e = list(existing)
    >>> e.remove(prefix + "2" + suffix)
    >>> _handle_clash2(existing=e, prefix=prefix, suffix=suffix)
    '00000.2.0000000000'
    """
    # calculate the longest possible string
    max_length = filename_max_length - len(prefix) - len(suffix)
    max_value = int("9" * max_length)
    # try to find a number
    final_name = None
    counter = 1
    while final_name is None:
        fullname = prefix + str(counter) + suffix
        if fullname.lower() not in existing:
            final_name = fullname
            break
        else:
            counter += 1
        if counter >= max_value:
            break
    # raise an error if nothing has been found
    if final_name is None:
        raise NameError("No unique name could be found.")
    # finished
    return final_name
