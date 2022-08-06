from setuptools import setup

setup(
    name="async_vkapi",
    version="1.0.0",
    description="Async vk api for python based on https://github.com/python273/vk_api/blob/master/vk_api/vk_api.py",
    url="https://github.com/dbealthy/async_vkapi.git",
    author="Bogatov Daniil",
    author_email="6ogatoff@gmail.com",
    license="BSD 2-clause",
    packages=["async_vkapi"],
    install_requires=["aiohttp"],
)
