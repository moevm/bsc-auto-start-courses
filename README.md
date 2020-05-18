## bsc-auto-start-courses

### how to run application

1. `docker build -t test-docker .`
2. `docker run -it --rm -p 80:80 --name <name> test-docker /bin/bash`
3. `service apache2 restart`
4. `service mongodb start`
5. `Открыть в браузере localhost`
