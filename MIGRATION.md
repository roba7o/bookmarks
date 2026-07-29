# Migration: make `bookmarks` a real package

You drive this one. Each step says *what* and *why*; the verification section at
the end is how you prove to yourself it worked.

Related: the lecture in `~/Documents/programmingSelfStudy/random/python_runtime/`
(Part 4.3 covers exactly this).

---

## The diagnosis

Your `pyproject.toml` declares a package called `bookmarks`. But run the build and
ask setuptools what it actually produced, and you get:

```
$ cat src/bookmarks.egg-info/top_level.txt
__init__
auth
exception_handlers
main
middleware
routes
schemas
settings
```

**There is no `bookmarks` in that list.** Your distribution is named `bookmarks`,
but it installs eight loose top-level modules instead of one package. (`__init__`
listed as a top-level module is the tell — that's `src/__init__.py` confusing
setuptools' auto-discovery.)

The cause: setuptools' src-layout discovery expects `src/<package_name>/`. You have
`src/<loose modules>`. So it treats every file in `src/` as its own top-level
module, and the editable install puts `src/` itself on `sys.path`.

That gives your project **two incompatible identities**:

| launched how | what's importable | does `from src.x import y` work? |
|---|---|---|
| via the install (`.pth` puts `src/` on the path) | `auth`, `main`, `schemas`, … | ✗ — there's no `src` on the path |
| from the repo root (cwd puts `bookmarks/` on the path) | `src`, `src.auth`, … | ✓ |

Your source is written for row 2. Your install produces row 1. That's why
everything works when you run from the repo root and falls over otherwise.

### Why it's worth fixing

**1. Name collisions.** `main`, `settings`, `auth`, `schemas` are about as generic
as names get. Any project that puts a directory containing its own `settings.py`
on the path will shadow yours, or vice versa. (Until ten minutes ago this was
machine-wide — the global install is now removed.)

**2. The duplicate-module bug.** Because one file is reachable under two names
(`schemas` and `src.schemas`), it can be executed twice in one process, producing
two module objects with two independent sets of globals. Two `metadata` objects,
two engines. Run `lab3_traps/double_import.py` in the lecture folder to watch it
happen — that lab is a three-file version of what your layout permits.

---

## Target shape

```
bookmarks/
├── pyproject.toml
└── src/
    └── bookmarks/          <- NEW: the actual package
        ├── __init__.py
        ├── main.py
        ├── auth.py
        ├── middleware.py
        ├── schemas.py
        ├── settings.py
        ├── exception_handlers.py
        └── routes/
            ├── __init__.py
            ├── auth.py
            └── bookmarks.py
```

`src/` becomes a *container* holding one package. That's its whole job — it exists
so your repo root is **not** importable by accident, which forces your imports to
be tested the same way a real install exposes them.

---

## Steps

Do this on a branch. `git status` is clean right now, so you have a clean point to
return to.

### 1. Move the files

```bash
git checkout -b package-layout
mkdir src/bookmarks
git mv src/auth.py src/exception_handlers.py src/main.py \
       src/middleware.py src/schemas.py src/settings.py \
       src/routes src/bookmarks/
git mv src/__init__.py src/bookmarks/__init__.py
```

After this, `src/` must contain **only** `bookmarks/`. Critically, `src/__init__.py`
must be gone — that file is what made `src` look like a package.

> Note: you'll now have `bookmarks.routes.bookmarks`. Legal, but if that reads
> badly to you, this is a cheap moment to rename it (`routes/bookmark_routes.py`
> or similar). Your call.

### 2. Rewrite the imports — 15 lines

Every `from src.X import Y` becomes `from bookmarks.X import Y`. Fifteen
occurrences across your files.

```bash
grep -rln "from src\.\|import src\." src/
```

Do the replacement however you like — editor find-and-replace is fine. **Read the
diff before committing.** The pattern to change is `src.` → `bookmarks.` *only*
in import statements; make sure you haven't caught a string literal or a comment.

### 3. Tell setuptools where the package is

Auto-discovery will now find it, but being explicit costs two lines and removes
the ambiguity that caused this. Add to `pyproject.toml`:

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

### 4. Reinstall so the metadata regenerates

```bash
uv sync --reinstall-package bookmarks
```

### 5. Update the launch commands

`Dockerfile` line 22 currently reads `uvicorn src.main:app`. It becomes
`uvicorn bookmarks.main:app`. Check `scripts/` and any notes in `docs/` for the
same string.

---

## Verification

Don't take "it starts" as proof. Each of these tests something specific.

**1. The package exists under the right name, from a directory with no relationship
to your project:**

```bash
cd /tmp && uv run --project ~/Documents/programmingSelfStudy/projects/bookmarks \
  python -c "import bookmarks.main; print(bookmarks.main.__file__)"
```

**2. The old identity is gone.** This should now fail — if `import schemas`
still succeeds, `src/` is still on the path and you've missed something:

```bash
cd /tmp && uv run --project ~/Documents/programmingSelfStudy/projects/bookmarks \
  python -c "import schemas"
# expect: ModuleNotFoundError
```

**3. The build metadata agrees.** After step 4:

```bash
cat src/bookmarks.egg-info/top_level.txt
# expect exactly one line: bookmarks
```

That file is the scoreboard. One line, one name, and the migration is done.

**4. The server runs from anywhere:**

```bash
cd /tmp && uv run --project ~/.../bookmarks uvicorn bookmarks.main:app --port 8000
```

---

## Check your understanding

Answer these before you start — they're the reasoning the steps are based on.

1. `src/__init__.py` is an empty file. Deleting it changes the behaviour of your
   whole project. Why can an empty file matter?

2. After the migration, the editable `.pth` file still contains one line pointing
   at `.../bookmarks/src`. It doesn't change at all. So what *did* change, such
   that `import bookmarks` now works and `import schemas` doesn't?

3. Verification step 2 asserts that something *stops* working. Why is that a
   better test than only checking that `import bookmarks.main` succeeds?

4. Your Dockerfile says `uvicorn src.main:app`. Given what uvicorn does with the
   string either side of the colon, predict the exact error you'd get if you
   migrated the code but forgot to update the Dockerfile.

---

## Rollback

```bash
git checkout main && git branch -D package-layout
uv sync --reinstall-package bookmarks
```
