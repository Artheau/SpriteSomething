FROM ubuntu

LABEL com.github.actions.name="Prepare for GitHub Releases"
LABEL com.github.actions.description="Prepare SpriteSomething for GitHub Releases"

COPY . .
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
