import uuid

from sqlalchemy import select, update, desc, or_, delete, and_
import datetime

from Databases.DB import *


async def get_users() -> list[User]:
    async with async_session() as session:
        users = await session.execute(
            select(User).where(and_(User.status == "info", User.status == "reserve")).order_by(desc(User.last_start_time))
        )
        users = users.scalars().all()

        return users


async def check_user(tele_id: str) -> User | None:
    async with async_session() as session:
        user = await session.execute(select(User).where(User.id == tele_id))
        user = user.scalar_one_or_none()

        return user


async def check_status(tele_id: str) -> list[str]:
    async with async_session() as session:
        user = await session.execute(select(User).where(User.id == tele_id))
        user = user.scalar_one()

        return user.status


async def update_status(tele_id: str, status: str, car_id: str | None = None):
    async with async_session() as session:
        await session.execute(update(User).where(User.id == tele_id).values(status=status))
        if car_id:
            await session.execute(update(User).where(User.id == tele_id).values(car_id=car_id))
        await session.commit()


async def update_last_start(tele_id: str):
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                update(User)
                .where(User.id == tele_id)
                .values(last_start_time=datetime.datetime.now())
            )
            await session.commit()


async def create_user(tele_id: str, username: str, lang: str):
    async with async_session() as session:
        async with session.begin():
            user = User(
                id=tele_id,
                username=username,
                lang=lang,
                last_start_time=datetime.datetime.now(),
            )

            session.add(user)
            await session.commit()

async def create_post_db(id: str):
    async with async_session() as session:
        async with session.begin():
            post = Post(
                id=id,
                images="",
                not_ready_images="",
                create_time=datetime.datetime.now(),
            )

            session.add(post)
            await session.commit()

async def delete_post_db(id: str):
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(Post).where(Post.id==id))
            await session.commit()

async def update_post_photo(id: str, photo_id: str, text: str = None):
    async with async_session() as session:
        async with session.begin():

            if text:
                await session.execute(update(Post).where(Post.id == id).values(not_ready_images=Post.not_ready_images+f"{photo_id}|",
                                                                               text=text))
            else:
                await session.execute(update(Post).where(Post.id == id).values(not_ready_images=Post.not_ready_images + f"{photo_id}|"))

            await session.commit()

async def update_post_documents(id: str, file_id: str, text: str = None):
    async with async_session() as session:
        async with session.begin():

            if text:
                await session.execute(update(Post).where(Post.id == id).values(information_files=Post.information_files+f"{file_id}|",
                                                                               information=text))
            else:
                await session.execute(update(Post).where(Post.id == id).values(information_files=Post.information_files + f"{file_id}|"))

            await session.commit()

async def update_post_photo_final(id: str, photo_ids: str):
    async with async_session() as session:
        async with session.begin():

            await session.execute(update(Post).where(Post.id == id).values(images=photo_ids))

            await session.commit()

async def update_post_name(id: str, name: str):
    async with async_session() as session:
        async with session.begin():

            await session.execute(update(Post).where(Post.id == id).values(car_name=name))

            await session.commit()

async def get_post_photos(id: str) -> list:
    async with async_session() as session:
        async with session.begin():

            post = await session.execute(select(Post).where(Post.id == id))
            post = post.scalar_one()

            return post.images.split("|")

async def get_not_ready_post_photos(id: str) -> list:
    async with async_session() as session:
        async with session.begin():

            post = await session.execute(select(Post).where(Post.id == id))
            post = post.scalar_one()

            return post.not_ready_images.split("|")

async def update_post_data(id: str, information: str, post_date: datetime, posted_status: bool = False):
    async with async_session() as session:
        async with session.begin():

            await session.execute(update(Post).where(Post.id == id).values(information=information,
                                                                           post_date=post_date,
                                                                           posted_status=posted_status))
            await session.commit()

async def update_post_status(id: str, posted_status: bool = False):
    async with async_session() as session:
        async with session.begin():

            await session.execute(update(Post).where(Post.id == id).values(posted_status=posted_status))
            await session.commit()

async def posting_cancel(id: str):
    async with async_session() as session:
        async with session.begin():

            await session.execute(update(Post).where(Post.id == id).values(post_date=None))
            await session.commit()

async def get_post(id: str) -> Post:
    async with async_session() as session:

        post = await session.execute(select(Post).where(Post.id == id))
        post = post.scalar_one()

        return post

async def get_posts() -> list[Post]:
    async with async_session() as session:

        posts = await session.execute(select(Post).order_by(desc(Post.create_time)))
        posts = posts.scalars().all()

        return posts

async def get_posts_for_posting() -> list[Post]:
    async with async_session() as session:

        posts = await session.execute(select(Post).where(and_(Post.posted_status == False, Post.post_date<=datetime.datetime.now())))
        posts = posts.scalars().all()

        return posts

async def update_post_upload_status(id: str):
    async with async_session() as session:
        async with session.begin():

            post = await session.execute(select(Post).where(Post.id == id))
            post = post.scalar_one()

            if post.upload_status == False:

                await session.execute(update(Post).where(Post.id == id).values(upload_status=True))
                await session.commit()
                return True
            else:
                return False

async def update_post_upload_status_(id: str, status: bool):
    async with async_session() as session:
        async with session.begin():

            await session.execute(update(Post).where(Post.id == id).values(upload_status=status))
            await session.commit()


async def update_post_information_upload_status(id: str):
    async with async_session() as session:
        async with session.begin():

            post = await session.execute(select(Post).where(Post.id == id))
            post = post.scalar_one()

            if post.upload_status == False:

                await session.execute(update(Post).where(Post.id == id).values(information_files_upload_status=True))
                await session.commit()
                return True
            else:
                return False

async def delete_user(tele_id: str):
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(User).where(User.id == tele_id))
            await session.commit()


async def create_bid(user_id: str, post_id: str):
    async with async_session() as session:
        async with session.begin():

            id = str(uuid.uuid4())

            bid = Bid(
                id=id,
                user_id = user_id,
                post_id = post_id,
                create_time = datetime.datetime.now(),
            )

            session.add(bid)
            await session.commit()

            return id

async def get_bid(bid_id: str) -> Bid | None:
    async with async_session() as session:
        bid = await session.execute(select(Bid).where(Bid.id == bid_id))
        bid = bid.scalar_one_or_none()

        return bid


async def delete_bid(bid_id: str):
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(Bid).where(Bid.id == bid_id))
            await session.commit()


async def find_bid(user_id: str, post_id: str) -> bool:
    async with async_session() as session:
        bid = await session.execute(select(Bid).where(and_(Bid.user_id == user_id, Bid.post_id == post_id)))
        bid = bid.scalar_one_or_none()

        return True if bid else False

