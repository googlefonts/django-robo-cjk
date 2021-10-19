# django-robo-cjk

`django-robo-cjk` is the server-side engine based on `python` and `django` that serves the [robo-cjk](https://github.com/BlackFoundryCom/black-robo-cjk) plugin.

Its purpose is to centralize and speed-up the design/development of CJK typefaces providing a whole set of APIs to manage `.rcjk` projects. 

## API

- [Globals](#globals)
- [Endpoints](#endpoints)
- [Client](#client)

### Globals

- Base URL: `http://164.90.229.235` *(temporary development environment, it will change very soon)*
- Authorization type: `Bearer Token` *(required by all APIs endpoints, except auth ones... :neckbeard:)*
- Request method: `POST`
- Response content type: `json`
- Success Response example :green_circle::
```javascript
{
    "data": {
        "name": "...",
        "status": "...",
        "...": "..."
    },
    "error": null,
    "status": 200
}
```
- Error response example :red_circle::
```javascript
{
    "data": null,
    "error": "Internal Server Error - Error description",
    "status": 500
}
```

### Endpoints

- [**Auth**](#auth)
   - [Auth **Token**](#auth-token)

- [**User**](#user)
   - [User **List**](#user-list)
   - [User **Me**](#user-me)

- [**Project**](#project)
   - [Project **List**](#project-list)
   - [Project **Get**](#project-get)
   - [Project **Create**](#project-create)
   
- [**Font**](#font)
   - [Font **List**](#font-list)
   - [Font **Get**](#font-get)
   - [Font **Create**](#font-create)
   - [Font **Update**](#font-update)
   
- [**Glyphs Composition**](#glyphs-composition)
   - [Glyphs Composition **Get**](#glyphs-composition-get)
   - [Glyphs Composition **Update**](#glyphs-composition-update)
   
- [**Glif**](#glif)
   - [Glif **List**](#glif-list)
   - [Glif **Lock**](#glif-lock)
   - [Glif **Unlock**](#glif-unlock)

- [**Atomic Element**](#atomic-element)
   - [Atomic Element **List**](#atomic-element-list)
   - [Atomic Element **Get**](#atomic-element-get)
   - [Atomic Element **Create**](#atomic-element-create)
   - [Atomic Element **Update**](#atomic-element-update)
   - [Atomic Element **Delete**](#atomic-element-delete)
   - [Atomic Element **Lock**](#atomic-element-lock)
   - [Atomic Element **Unlock**](#atomic-element-unlock)

- [**Atomic Element Layer**](#atomic-element-layer)
   - [Atomic Element Layer **Create**](#atomic-element-layer-create)
   - [Atomic Element Layer **Rename**](#atomic-element-layer-rename)
   - [Atomic Element Layer **Update**](#atomic-element-layer-update)
   - [Atomic Element Layer **Delete**](#atomic-element-layer-delete)

- [**Deep Component**](#deep-component)
   - [Deep Component **List**](#deep-component-list)
   - [Deep Component **Get**](#deep-component-get)
   - [Deep Component **Create**](#deep-component-create)
   - [Deep Component **Update**](#deep-component-update)
   - [Deep Component **Delete**](#deep-component-delete)
   - [Deep Component **Lock**](#deep-component-lock)
   - [Deep Component **Unlock**](#deep-component-unlock)

- [**Character Glyph**](#character-glyph)
   - [Character Glyph **List**](#character-glyph-list)
   - [Character Glyph **Get**](#character-glyph-get)
   - [Character Glyph **Create**](#character-glyph-create)
   - [Character Glyph **Update**](#character-glyph-update)
   - [Character Glyph **Delete**](#character-glyph-delete)
   - [Character Glyph **Lock**](#character-glyph-lock)
   - [Character Glyph **Unlock**](#character-glyph-unlock)

- [**Character Glyph Layer**](#character-glyph-layer)
   - [Character Glyph Layer **Create**](#character-glyph-layer-create)
   - [Character Glyph Layer **Rename**](#character-glyph-layer-rename)
   - [Character Glyph Layer **Update**](#character-glyph-layer-update)
   - [Character Glyph Layer **Delete**](#character-glyph-layer-delete)

---

### Auth

#### Auth Token

##### Request

| URL | Method |
|---|---|
| `/api/auth/token/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `username` | `string` | yes |
| `password` | `string` | yes |

##### Response

```javascript
{
    "data": {
        "auth_token": "eyJ0..."
    },
    "error": null,
    "status": 200
}
```

---

### User

#### User List

##### Request

| URL | Method |
|---|---|
| `/api/user/list/` | `POST` |

##### Response

```javascript
{
    "data": [
        {
            "email": "fabio.caccamo@black-foundry.com",
            "first_name": "Fabio",
            "id": 1,
            "last_name": "Caccamo",
            "username": "fabio.caccamo"
        },
        {
            "email": "jeremie.hornus@black-foundry.com",
            "first_name": "Jeremie",
            "id": 2,
            "last_name": "Hornus",
            "username": "jeremie.hornus"
        },
        {
            "email": "gaetan.baehr@black-foundry.com",
            "first_name": "Gaetan",
            "id": 3,
            "last_name": "Baehr",
            "username": "gaetan.baehr"
        },
        // ...
    ],
    "error": null,
    "status": 200
}
```

---

#### User Me

##### Request

| URL | Method |
|---|---|
| `/api/user/me/` | `POST` |

##### Response

```javascript
{
    "data": {
        "email": "fabio.caccamo@black-foundry.com",
        "first_name": "Fabio",
        "id": 1,
        "last_name": "Caccamo",
        "username": "fabio.caccamo"
    },
    "error": null,
    "status": 200
}
```

---

### Project

#### Project List

##### Request

| URL | Method |
|---|---|
| `/api/project/list/` | `POST` |

<!--
| Param | Type | Required |
|---|---|---|
| | | |
-->

##### Response

```javascript
{
    "data": [
        {
            "name": "GS",
            "repo_url": "https://github.com/BlackFoundryCom/gs-cjk-rcjk",
            "repo_branch": "master",
            "slug": "gs",
            "uid": "fde4fc80-c136-4e2f-a9be-c80e18b9f213"
        }
    ],
    "error": null,
    "status": 200
}
```

---

#### Project Get

##### Request

| URL | Method |
|---|---|
| `/api/project/get/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `project_uid` | `string` | yes |

##### Response

```javascript
{
    "data": {
        "name": "GS",
        "repo_url": "https://github.com/BlackFoundryCom/gs-cjk-rcjk",
        "repo_branch": "master",
        "slug": "gs",
        "uid": "fde4fc80-c136-4e2f-a9be-c80e18b9f213"
    },
    "error": null,
    "status": 200
}
```

---

#### Project Create

##### Request

| URL | Method |
|---|---|
| `/api/project/create/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `name` | `string` | yes |
| `repo_url` | `string` | yes |
| `repo_branch` | `string` | no |

##### Response

See [Project Get](#project-get) response.

---

### Font

#### Font List

##### Request

| URL | Method |
|---|---|
| `/api/font/list/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `project_uid` | `string` | yes |

##### Response

```javascript
{
    "data": [
        {
            "name": "Hanzi",
            "project_id": 1,
            "slug": "hanzi",
            "uid": "cbac1f2d-6b6c-46a4-a477-798d49042ff4"
        }
    ],
    "error": null,
    "status": 200
}
```

---

#### Font Get

##### Request

| URL | Method |
|---|---|
| `/api/font/get/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |

##### Response

```javascript
{
    "data": {
        "fontlib": {
            "CJKDesignFrameSettings": {
                "characterFace": 90,
                "customsFrames": [],
                "em_Dimension": [
                    1000,
                    1000
                ],
                "horizontalLine": 15,
                "overshoot": [
                    20,
                    20
                ],
                "type": "han",
                "verticalLine": 15
            },
            "com.typemytype.robofont.guideline.magnetic.bj4ZrgHhis": 5,
            "com.typemytype.robofont.guideline.showMeasurements.bj4ZrgHhis": false,
            "com.typemytype.robofont.segmentType": "curve",
            "robocjk.defaultGlyphWidth": 1000,
            "robocjk.fontVariations": [
                "wght"
            ]
        },
        "features": "...",
        "designspace": {
            "axes": [
                {
                    "name": "Weight",
                    "tag": "wght",
                    "minValue": 400,
                    "defaultValue": 400,
                    "maxValue": 700
                }
            ]
        },
        "name": "Hanzi",
        "slug": "hanzi",
        "uid": "cbac1f2d-6b6c-46a4-a477-798d49042ff4"
    },
    "error": null,
    "status": 200
}
```

---

#### Font Create

##### Request

| URL | Method |
|---|---|
| `/api/font/create/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `project_uid` | `string` | yes |
| `name` | `string` | yes |
| `fontlib` | `json` | no |
| `features` | `string` | no |
| `designspace` | `json` | no |

##### Response

See [Font Get](#font-get) response.

---

#### Font Update

##### Request

| URL | Method |
|---|---|
| `/api/font/update/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `fontlib` | `json` | no |
| `features` | `string` | no |
| `designspace` | `json` | no |

##### Response

See [Font Get](#font-get) response.

---

#### Glyphs Composition Get

##### Request

| URL | Method |
|---|---|
| `/api/glyphs-composition/get/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |

##### Response

```javascript
{
    "data": {
        "\u2e80": "\u4e36\u4e36", 
        "\u2e84": "\u2e84", 
        // ...
    },
    "error": null,
    "status": 200
}
```

---

#### Glyphs Composition Update

##### Request

| URL | Method |
|---|---|
| `/api/glyphs-composition/update/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `data` | `string` | yes |

##### Response

See [Glyphs Composition Get](#glyphs-composition-get) response.

---

### Glif

#### Glif List

##### Request

| URL | Method |
|---|---|
| `/api/glif/list/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `status` | `string` | no |
| `updated_by_current_user` | `bool` | no |
| `updated_by` | `int` | no |
| `is_locked_by_current_user` | `bool` | no |
| `is_locked_by` | `int` | no |
| `is_locked` | `bool` | no |
| `is_empty` | `bool` | no |
| `has_variation_axis` | `bool` | no |
| `has_outlines` | `bool` | no |
| `has_components` | `bool` | no |
| `has_unicode` | `bool` | no |

##### Response

```javascript
{
    "data": {
        "atomic_elements": [
            {
                "id": 1,
                "name": "..."
            },
            {
                "id": 2,
                "name": "..."
            }
        ],
        "deep_components": [
            {
                "id": 1,
                "name": "..."
            },
            {
                "id": 2,
                "name": "..."
            }
        ],
        "character_glyphs": [
            {
                "id": 1,
                "name": "..."
            },
            {
                "id": 2,
                "name": "..."
            }
        ],
    },
    "error": null,
    "status": 200
```

---

#### Glif Lock

Lock multiple glifs at once.

##### Request

| URL | Method |
|---|---|
| `/api/glif/lock/` | `POST` |

| Param | Type | Required | Description |
|---|---|---|---|
| `font_uid` | `string` | yes | |
| `atomic_elements` | `string` | no | comma-separated list of names or ids |
| `deep_components` | `string` | no | comma-separated list of names or ids |
| `character_glyphs` | `string` | no | comma-separated list of names or ids |

##### Response

```javascript
{
    "data": {
        "atomic_elements": [
            {
                "id": 1,
                "name": "..."
            },
            {
                "id": 2,
                "name": "..."
            }
        ],
        "deep_components": [
            {
                "id": 1,
                "name": "..."
            },
            {
                "id": 2,
                "name": "..."
            }
        ],
        "character_glyphs": [
            {
                "id": 1,
                "name": "..."
            },
            {
                "id": 2,
                "name": "..."
            }
        ],
    },
    "error": null,
    "status": 200
```

---

#### Glif Unlock

Unlock multiple glifs at once.

##### Request

| URL | Method |
|---|---|
| `/api/glif/unlock/` | `POST` |

| Param | Type | Required | Description |
|---|---|---|---|
| `font_uid` | `string` | yes | |
| `atomic_elements` | `string` | no | comma-separated list of names or ids |
| `deep_components` | `string` | no | comma-separated list of names or ids |
| `character_glyphs` | `string` | no | comma-separated list of names or ids |

##### Response

```javascript
{
    "data": {
        "atomic_elements": [
            {
                "id": 1,
                "name": "..."
            },
            {
                "id": 2,
                "name": "..."
            }
        ],
        "deep_components": [
            {
                "id": 1,
                "name": "..."
            },
            {
                "id": 2,
                "name": "..."
            }
        ],
        "character_glyphs": [
            {
                "id": 1,
                "name": "..."
            },
            {
                "id": 2,
                "name": "..."
            }
        ],
    },
    "error": null,
    "status": 200
```

---

### Atomic Element

#### Atomic Element List

##### Request

| URL | Method |
|---|---|
| `/api/atomic-element/list/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `status` | `string` | no |
| `updated_by_current_user` | `bool` | no |
| `updated_by` | `int` | no |
| `is_locked_by_current_user` | `bool` | no |
| `is_locked_by` | `int` | no |
| `is_locked` | `bool` | no |
| `is_empty` | `bool` | no |
| `has_variation_axis` | `bool` | no |
| `has_outlines` | `bool` | no |
| `has_components` | `bool` | no |

##### Response

```javascript
{
    "data": [
        {
            "id": 1,
            "name": "bendingBoth"
        },
        {
            "id": 2,
            "name": "bendingBothOp"
        },
        {
            "id": 3,
            "name": "bendingBothRev"
        }
    ],
    "error": null,
    "status": 200
}
```

---

#### Atomic Element Get

##### Request

| URL | Method |
|---|---|
| `/api/atomic-element/get/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |

`*` an Atomic Element can be retrieved by `id` or by `name`, **only one of these parameters is required**.

##### Response

```javascript
{
    "data": {
        "data": "<?xml version='1.0' encoding='UTF-8'?>\n<glyph name=\"curvedStroke\" format=\"2\">\n ... \n</glyph>\n",
        "filename": "curvedS_troke.glif",
        "has_components": false,
        "has_outlines": true,
        "has_unicode": false,
        "has_variation_axis": true,
        "id": 83,
        "is_empty": false,
        "is_locked": false,
        "layers": [
            {
                "data": "<?xml version='1.0' encoding='UTF-8'?>\n<glyph name=\"curvedStroke\" format=\"2\">\n ... \n</glyph>\n",
                "filename": "curvedS_troke.glif",
                "glif_id": 83,
                "group_name": "1",
                "has_components": false,
                "has_outlines": true,
                "has_unicode": false,
                "has_variation_axis": false,
                "id": 772,
                "is_empty": false,
                "name": "curvedStroke"
            },
            {
                "data": "<?xml version='1.0' encoding='UTF-8'?>\n<glyph name=\"curvedStroke\" format=\"2\">\n ... \n</glyph>\n",
                "filename": "curvedS_troke.glif",
                "glif_id": 83,
                "group_name": "2",
                "has_components": false,
                "has_outlines": false,
                "has_unicode": false,
                "has_variation_axis": false,
                "id": 926,
                "is_empty": true,
                "name": "curvedStroke"
            }
        ],
        "locked_at": null,
        "locked_by_id": null,
        "locked_by_user": null,
        "made_of": [],
        "name": "curvedStroke",
        "status": "wip",
        "type": "Atomic Element",
        "type_code": "AE",
        "unicode_hex": "",
        "used_by": [
            {
                "id": 896,
                "name": "DC_20041_00"
            },
            {
                "id": 638,
                "name": "DC_4EA1_01"
            },
            {
                "id": 907,
                "name": "DC_76F4_00"
            }
        ]
    },
    "error": null,
    "status": 200
}
```

---

#### Atomic Element Create

The created Atomic Element is automatically locked by the current user.

##### Request

| URL | Method |
|---|---|
| `/api/atomic-element/create/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `data` | `string` | yes |

- `data` is the Atomic Element `.glif` file data in `xml` format.

##### Response

See [Atomic Element Get](#atomic-element-get) response.

---

#### Atomic Element Update

##### Request

| URL | Method |
|---|---|
| `/api/atomic-element/update/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |
| `data` | `string` | yes |

- `*` Atomic Element can be retrieved by `id` or by `name`, **only one of these parameters is required**.
- `data` is the Atomic Element `.glif` file data in `xml` format.

##### Response

See [Atomic Element Get](#atomic-element-get) response.

---

#### Atomic Element Delete

##### Request

| URL | Method |
|---|---|
| `/api/atomic-element/delete/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |

- `*` Atomic Element can be retrieved by `id` or by `name`, **only one of these parameters is required**.

##### Response

```javascript
{
    "data": [
        1,
        {
            "robocjk.AtomicElement": 1
        }
    ],
    "error": null,
    "status": 200
}
```

---

#### Atomic Element Lock

##### Request

| URL | Method |
|---|---|
| `/api/atomic-element/lock/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |

- `*` Atomic Element can be retrieved by `id` or by `name`, **only one of these parameters is required**.

##### Response

See [Atomic Element Get](#atomic-element-get) response.

---

#### Atomic Element Unlock

##### Request

| URL | Method |
|---|---|
| `/api/atomic-element/unlock/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |

- `*` Atomic Element can be retrieved by `id` or by `name`, **only one of these parameters is required**.

##### Response

See [Atomic Element Get](#atomic-element-get) response.

---

### Atomic Element Layer

#### Atomic Element Layer Create

##### Request

| URL | Method |
|---|---|
| `/api/atomic-element/layer/create/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `atomic_element_id` | `int` | yes `*` |
| `atomic_element_name` | `string` | yes `*` |
| `group_name` | `string` | yes |
| `data` | `string` | yes |

- `*` the parent Atomic Element can be retrieved by `atomic_element_id` or by `atomic_element_name`, **only one of these parameters is required**.

##### Response

See [Atomic Element Get](#atomic-element-get) response.

---

#### Atomic Element Layer Rename

##### Request

| URL | Method |
|---|---|
| `/api/atomic-element/layer/rename/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `atomic_element_id` | `int` | yes `*` |
| `atomic_element_name` | `string` | yes `*` |
| `id` | `int` | yes `**` |
| `group_name` | `string` | yes `**` |
| `new_group_name` | `string` | yes |

- `*` the parent Atomic Element can be retrieved by `atomic_element_id` or by `chaatomic_element_nameracter_glyph_name`, **only one of these parameters is required**.
- `**` the Atomic Element Layer can be retrieved by `id` or by `group_name`, **only one of these parameters is required**.

##### Response

See [Character Glyph Get](#character-glyph-get) response.

---

#### Atomic Element Layer Update

##### Request

| URL | Method |
|---|---|
| `/api/atomic-element/layer/update/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `atomic_element_id` | `int` | yes `*` |
| `atomic_element_name` | `string` | yes `*` |
| `id` | `int` | yes `**` |
| `group_name` | `string` | yes `**` |
| `data` | `string` | yes |

- `*` the parent Atomic Element can be retrieved by `atomic_element_id` or by `atomic_element_name`, **only one of these parameters is required**.
- `**` the Atomic Element Layer can be retrieved by `id` or by `group_name`, **only one of these parameters is required**.

##### Response

See [Atomic Element Get](#atomic-element-get) response.

---

#### Atomic Element Layer Delete

##### Request

| URL | Method |
|---|---|
| `/api/atomic-element/layer/delete/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `atomic_element_id` | `int` | yes `*` |
| `atomic_element_name` | `string` | yes `*` |
| `id` | `int` | yes `**` |
| `group_name` | `string` | yes `**` |

- `*` the parent Atomic Element can be retrieved by `atomic_element_id` or by `atomic_element_name`, **only one of these parameters is required**.
- `**` the Atomic Element Layer can be retrieved by `id` or by `group_name`, **only one of these parameters is required**.

##### Response

```javascript
{
    "data": [
        1,
        {
            "robocjk.AtomicElementLayer": 1
        }
    ],
    "error": null,
    "status": 200
}
```

---

### Deep Component

#### Deep Component List

##### Request

| URL | Method |
|---|---|
| `/api/deep-component/list/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `status` | `string` | no |
| `updated_by_current_user` | `bool` | no |
| `updated_by` | `int` | no |
| `is_locked_by_current_user` | `bool` | no |
| `is_locked_by` | `int` | no |
| `is_locked` | `bool` | no |
| `is_empty` | `bool` | no |
| `has_variation_axis` | `bool` | no |
| `has_outlines` | `bool` | no |
| `has_components` | `bool` | no |

##### Response

```javascript
{
    "data": [
        {
            "id": 1,
            "name": "DC_20041_00"
        },
        {
            "id": 2,
            "name": "DC_20041_01"
        },
        {
            "id": 3,
            "name": "DC_20086_00"
        }
    ],
    "error": null,
    "status": 200
}
```

---

#### Deep Component Get

##### Request

| URL | Method |
|---|---|
| `/api/deep-component/get/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |

`*` an Deep Component can be retrieved by `id` or by `name`, **only one of these parameters is required**.

##### Response

```javascript
{
    "data": {
        "data": "<?xml version='1.0' encoding='UTF-8'?>\n<glyph name=\"DC_24D13_00\" format=\"2\"> ... </glyph>\n",
        "filename": "D_C__24D_13_00.glif",
        "has_components": true,
        "has_outlines": false,
        "has_unicode": false,
        "has_variation_axis": true,
        "id": 493,
        "is_empty": false,
        "is_locked": false,
        "layers": [],
        "locked_at": null,
        "locked_by_id": null,
        "locked_by_user": null,
        "made_of": [
            {
                "data": "<?xml version='1.0' encoding='UTF-8'?>\n<glyph name=\"bendingBoth\" format=\"2\"> ... </glyph>\n",
                "filename": "bendingB_oth.glif",
                "has_components": false,
                "has_outlines": true,
                "has_unicode": false,
                "has_variation_axis": true,
                "id": 88,
                "is_empty": false,
                "is_locked": false,
                "locked_at": null,
                "locked_by_id": null,
                "name": "bendingBoth",
                "status": "wip",
                "unicode_hex": ""
            },
            {
                "data": "<?xml version='1.0' encoding='UTF-8'?>\n<glyph name=\"line\" format=\"2\"> ... </glyph>\n",
                "filename": "line.glif",
                "has_components": false,
                "has_outlines": true,
                "has_unicode": false,
                "has_variation_axis": true,
                "id": 79,
                "is_empty": false,
                "is_locked": false,
                "locked_at": null,
                "locked_by_id": null,
                "name": "line",
                "status": "wip",
                "unicode_hex": ""
            },
            {
                "data": "<?xml version='1.0' encoding='UTF-8'?>\n<glyph name=\"pingNa\" format=\"2\"> ... </glyph>\n",
                "filename": "pingN_a.glif",
                "has_components": false,
                "has_outlines": true,
                "has_unicode": false,
                "has_variation_axis": true,
                "id": 102,
                "is_empty": false,
                "is_locked": false,
                "locked_at": null,
                "locked_by_id": null,
                "name": "pingNa",
                "status": "wip",
                "unicode_hex": ""
            }
        ],
        "name": "DC_24D13_00",
        "status": "wip",
        "type": "Deep Component",
        "type_code": "DC",
        "unicode_hex": "",
        "used_by": []
    },
    "error": null,
    "status": 200
}
```

---

#### Deep Component Create

The created Deep Component is automatically locked by the current user.

##### Request

| URL | Method |
|---|---|
| `/api/deep-component/create/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `data` | `string` | yes |

- `data` is the Deep Component `.glif` file data in `xml` format.

##### Response

See [Deep Component Get](#deep-component-get) response.

---

#### Deep Component Update

##### Request

| URL | Method |
|---|---|
| `/api/deep-component/update/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |
| `data` | `string` | yes |

- `*` Deep Component can be retrieved by `id` or by `name`, **only one of these parameters is required**.
- `data` is the Deep Component `.glif` file data in `xml` format.

##### Response

See [Deep Component Get](#deep-component-get) response.

---

#### Deep Component Delete

##### Request

| URL | Method |
|---|---|
| `/api/deep-component/delete/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |

- `*` Deep Component can be retrieved by `id` or by `name`, **only one of these parameters is required**.

##### Response

```javascript
{
    "data": [
        1,
        {
            "robocjk.DeepComponent": 1
        }
    ],
    "error": null,
    "status": 200
}
```

---

#### Deep Component Lock

##### Request

| URL | Method |
|---|---|
| `/api/deep-component/lock/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |

- `*` Deep Component can be retrieved by `id` or by `name`, **only one of these parameters is required**.

##### Response

See [Deep Component Get](#deep-component-get) response.

---

#### Deep Component Unlock

##### Request

| URL | Method |
|---|---|
| `/api/deep-component/unlock/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |

- `*` Deep Component can be retrieved by `id` or by `name`, **only one of these parameters is required**.

##### Response

See [Deep Component Get](#deep-component-get) response.

---

### Character Glyph

#### Character Glyph List

##### Request

| URL | Method |
|---|---|
| `/api/character-glyph/list/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `status` | `string` | no |
| `updated_by_current_user` | `bool` | no |
| `updated_by` | `int` | no |
| `is_locked_by_current_user` | `bool` | no |
| `is_locked_by` | `int` | no |
| `is_locked` | `bool` | no |
| `is_empty` | `bool` | no |
| `has_variation_axis` | `bool` | no |
| `has_outlines` | `bool` | no |
| `has_components` | `bool` | no |
| `has_unicode` | `bool` | no |

##### Response

```javascript
{
    "data": [
        {
            "id": 1,
            "name": "uni000A",
            "unicode_hex": "000A"
        },
        {
            "id": 2,
            "name": "uni000D",
            "unicode_hex": "000D"
        },
        {
            "id": 3,
            "name": "uni20041",
            "unicode_hex": ""
        }
    ],
    "error": null,
    "status": 200
}
```

---

#### Character Glyph Get

##### Request

| URL | Method |
|---|---|
| `/api/character-glyph/get/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |

`*` an Character Glyph can be retrieved by `id` or by `name`, **only one of these parameters is required**.

##### Response

```javascript
{
    "data": {
        "data": "<?xml version='1.0' encoding='UTF-8'?>\n<glyph name=\"uni2EBB\" format=\"2\"> ... </glyph>\n",
        "filename": "uni2E_B_B_.glif",
        "has_components": true,
        "has_outlines": false,
        "has_unicode": true,
        "has_variation_axis": false,
        "id": 26281,
        "is_empty": false,
        "is_locked": false,
        "layers": [],
        "locked_at": null,
        "locked_by_id": null,
        "locked_by_user": null,
        "made_of": [
            {
                "data": "<?xml version='1.0' encoding='UTF-8'?>\n<glyph name=\"DC_4E00_00\" format=\"2\"> ... </glyph>\n",
                "filename": "D_C__4E_00_00.glif",
                "has_components": true,
                "has_outlines": false,
                "has_unicode": false,
                "has_variation_axis": true,
                "id": 681,
                "is_empty": false,
                "is_locked": false,
                "locked_at": null,
                "locked_by_id": null,
                "name": "DC_4E00_00",
                "status": "wip",
                "unicode_hex": ""
            },
            {
                "data": "<?xml version='1.0' encoding='UTF-8'?>\n<glyph name=\"DC_8080_00\" format=\"2\"> ... </glyph>\n",
                "filename": "D_C__8080_00.glif",
                "has_components": true,
                "has_outlines": false,
                "has_unicode": false,
                "has_variation_axis": true,
                "id": 777,
                "is_empty": false,
                "is_locked": false,
                "locked_at": null,
                "locked_by_id": null,
                "name": "DC_8080_00",
                "status": "wip",
                "unicode_hex": ""
            }
        ],
        "name": "uni2EBB",
        "status": "wip",
        "type": "Character Glyph",
        "type_code": "CG",
        "unicode_hex": "2EBB",
        "used_by": []
    },
    "error": null,
    "status": 200
}
```

---

#### Character Glyph Create

The created Character Glyph is automatically locked by the current user.

##### Request

| URL | Method |
|---|---|
| `/api/character-glyph/create/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `data` | `string` | yes |

- `data` is the Character Glyph `.glif` file data in `xml` format.

##### Response

See [Character Glyph Get](#character-glyph-get) response.

---

#### Character Glyph Update

##### Request

| URL | Method |
|---|---|
| `/api/character-glyph/update/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |
| `data` | `string` | yes |

- `*` Character Glyph can be retrieved by `id` or by `name`, **only one of these parameters is required**.
- `data` is the Character Glyph `.glif` file data in `xml` format.

##### Response

See [Character Glyph Get](#character-glyph-get) response.

---

#### Character Glyph Delete

##### Request

| URL | Method |
|---|---|
| `/api/character-glyph/delete/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |

- `*` Character Glyph can be retrieved by `id` or by `name`, **only one of these parameters is required**.

##### Response

```javascript
{
    "data": [
        1,
        {
            "robocjk.CharacterGlyph": 1
        }
    ],
    "error": null,
    "status": 200
}
```

---

#### Character Glyph Lock

##### Request

| URL | Method |
|---|---|
| `/api/character-glyph/lock/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |

- `*` Character Glyph can be retrieved by `id` or by `name`, **only one of these parameters is required**.

##### Response

See [Character Glyph Get](#character-glyph-get) response.

---

#### Character Glyph Unlock

##### Request

| URL | Method |
|---|---|
| `/api/character-glyph/unlock/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `id` | `int` | yes `*` |
| `name` | `string` | yes `*` |

- `*` Character Glyph can be retrieved by `id` or by `name`, **only one of these parameters is required**.

##### Response

See [Character Glyph Get](#character-glyph-get) response.

---

### Character Glyph Layer

#### Character Glyph Layer Create

##### Request

| URL | Method |
|---|---|
| `/api/character-glyph/layer/create/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `character_glyph_id` | `int` | yes `*` |
| `character_glyph_name` | `string` | yes `*` |
| `group_name` | `string` | yes |
| `data` | `string` | yes |

- `*` the parent Character Glyph can be retrieved by `character_glyph_id` or by `character_glyph_name`, **only one of these parameters is required**.

##### Response

See [Character Glyph Get](#character-glyph-get) response.

---

#### Character Glyph Layer Rename

##### Request

| URL | Method |
|---|---|
| `/api/character-glyph/layer/rename/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `character_glyph_id` | `int` | yes `*` |
| `character_glyph_name` | `string` | yes `*` |
| `id` | `int` | yes `**` |
| `group_name` | `string` | yes `**` |
| `new_group_name` | `string` | yes |

- `*` the parent Character Glyph can be retrieved by `character_glyph_id` or by `character_glyph_name`, **only one of these parameters is required**.
- `**` the Character Glyph Layer can be retrieved by `id` or by `group_name`, **only one of these parameters is required**.

##### Response

See [Character Glyph Get](#character-glyph-get) response.

---

#### Character Glyph Layer Update

##### Request

| URL | Method |
|---|---|
| `/api/character-glyph/layer/update/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `character_glyph_id` | `int` | yes `*` |
| `character_glyph_name` | `string` | yes `*` |
| `id` | `int` | yes `**` |
| `group_name` | `string` | yes `**` |
| `data` | `string` | yes |

- `*` the parent Character Glyph can be retrieved by `character_glyph_id` or by `character_glyph_name`, **only one of these parameters is required**.
- `**` the Character Glyph Layer can be retrieved by `id` or by `group_name`, **only one of these parameters is required**.

##### Response

See [Character Glyph Get](#character-glyph-get) response.

---

#### Character Glyph Layer Delete

##### Request

| URL | Method |
|---|---|
| `/api/character-glyph/layer/delete/` | `POST` |

| Param | Type | Required |
|---|---|---|
| `font_uid` | `string` | yes |
| `character_glyph_id` | `int` | yes `*` |
| `character_glyph_name` | `string` | yes `*` |
| `id` | `int` | yes `**` |
| `group_name` | `string` | yes `**` |

- `*` the parent Character Glyph can be retrieved by `character_glyph_id` or by `character_glyph_name`, **only one of these parameters is required**.
- `**` the Character Glyph Layer can be retrieved by `id` or by `group_name`, **only one of these parameters is required**.

##### Response

```javascript
{
    "data": [
        1,
        {
            "robocjk.CharacterGlyphLayer": 1
        }
    ],
    "error": null,
    "status": 200
}
```

---

### Client

There is client that is possible to use to interact with APIs easily. 

**Using the client all the API endpoints are available as methods and the authentication token will be managed/renewed automatically.**

Usage:
```python
from robocjk.api.client import Client

c = Client(
    host='https://...', 
    username='<username>', 
    password='<password>')
    
response = c.user_me()
print(response)
```
