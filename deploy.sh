rsync -av --exclude='.git' --exclude='.gitignore' --exclude='deploy.sh' --exclude='*db' --exclude='__pycache__' --exclude='__pycache__/*' --exclude='venv' --exclude='venv/*' --exclude='test' --exclude='test/*' --exclude='ENV_DIR/*' /home/jtbooth/dev/homework/* jt@jtbooth.com:/home/jt/iroha