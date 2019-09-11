FROM ubuntu

LABEL com.github.actions.name="Prepare Binary Artifact"
LABEL com.github.actions.description="Prepare SpriteSomething Binary for Artifact storage"

COPY . .
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
