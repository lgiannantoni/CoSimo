from setuptools import setup

setup(
   name='cosimo',
   version='1.0.0-alpha',
   author='Leonardo Giannantoni',
   author_email='leonardo.giannantoni@gmail.com',
   packages=['cosimo'],
   scripts=[],
   url='http://github.com/leonardogian/CoSimo',
   #license='LICENSE',
   #description='',
   long_description=open('README.md').read(),
   install_requires=[
       'Pyro4~=4.80',
       'fabric~=2.6.0'
   ],
)