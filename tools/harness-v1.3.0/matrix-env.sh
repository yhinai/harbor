# Source from a shell on matrix. Does not change the default Docker context.
export PATH="$HOME/.local/harbor-runtime/bin:$PATH"
export DOCKER_CONFIG="$HOME/.local/harbor-runtime/docker-config"
export DOCKER_HOST="unix://$HOME/.colima/frontier-portfolio/docker.sock"
