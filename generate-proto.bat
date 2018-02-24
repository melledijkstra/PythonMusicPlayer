@echo off
echo Generating proto grpc files...
python -m grpc_tools.protoc -I=proto --python_out=mpserver/grpc --grpc_python_out=mpserver/grpc proto/mmp.proto
echo DONE
