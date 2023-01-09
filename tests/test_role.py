"""Test roles and linking"""
from typing import AsyncGenerator
import logging

import pytest
import pytest_asyncio
from asyncpg.exceptions import UniqueViolationError

from arkia11nmodels.models import Role, User
from arkia11nmodels.models.role import UserRole
from .test_token import with_user  # pylint: disable=W0611 # false positive

LOGGER = logging.getLogger(__name__)

# pylint: disable=W0621


@pytest_asyncio.fixture(scope="module")
async def with_role(dockerdb: str) -> AsyncGenerator[User, None]:
    """Create a role for tests"""
    _ = dockerdb  # consume the fixture to keep linter happy
    role = Role(displayname="Testing role")
    await role.create()
    yield role
    await UserRole.delete.where(UserRole.role == role.pk).gino.status()  # Nuke leftovers
    await role.delete()


@pytest.mark.asyncio
async def test_role_fixture(with_role: Role) -> None:
    """Just test the fixture"""
    assert with_role.displayname == "Testing role"


@pytest.mark.asyncio
async def test_role_crud() -> None:
    """Test that we can Create, Read, Update and Delete Roles"""
    # Create
    role = Role(displayname="Testing role")
    await role.create()
    assert isinstance(role.acl, list)
    assert not role.acl
    role_pk = str(role.pk)
    LOGGER.debug("role={}".format(role.to_dict()))

    new_acl = list(role.acl)
    new_acl.append({"target": "fi.pvarki.dummyservicle:read", "action": "grant"})
    await role.update(acl=new_acl).apply()

    fetched = await Role.get(role_pk)
    LOGGER.debug("fetched={}".format(fetched.to_dict()))
    assert fetched.created != fetched.updated
    assert fetched.acl[0]["target"] == "fi.pvarki.dummyservicle:read"

    # Delete
    await role.delete()
    fetched = await Role.get(role_pk)
    assert fetched is None


@pytest.mark.asyncio
async def test_role_assign_remove(with_user: User, with_role: Role) -> None:
    """Check that the helpers work"""
    assert await with_role.assign_to(with_user)
    assert not await with_role.assign_to(with_user)
    assert await with_role.remove_from(with_user)
    assert not await with_role.remove_from(with_user)


@pytest.mark.asyncio
async def test_userrole_unique(with_user: User, with_role: Role) -> None:
    """Make sure the uniqueness is enforces"""
    link1 = UserRole(role=with_role.pk, user=with_user.pk)
    await link1.create()

    with pytest.raises(UniqueViolationError):
        link2 = UserRole(role=with_role.pk, user=with_user.pk)
        await link2.create()

    await link1.delete()