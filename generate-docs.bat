@echo off
set currdir = %cd%
cd docs
make html
cd %currdir%
