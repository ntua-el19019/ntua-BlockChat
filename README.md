# ntua-blockchain 2023-24

<p align="center">
  <img src="./images/logo.png" max-width="50%" />
</p>

#### BlockChat

# To-Do List
- [ ] Run the code and debug
- [X] Websockets/endpoints
- [X] app.py/main.py file
- [X] client/blockchat.py file

Implement the following functions:
- [x] generate_wallet()
- [x] create_transaction()
- [x] broadcast_transaction()
- [x] broadcast_block()
- [x] validate_chain()
- [x] stake(amount)


#### Build and Run Your Docker Containers:

1. From home directory (where docker-compose.yml and Dockerfile reside) run:

```  docker build -t ntua-blockchain . ```

2. Create network:

``` docker network create --subnet=172.18.0.0/16 ntua-blockchain_blockchat ```

3. Run each docker container with this command:

For bootstrap node:

```docker run -it -e PORT=8001 -e IP=172.18.0.3 -p 8001:8000 --network ntua-blockchain_blockchat --rm ntua-blockchain```

4. Run each client docker container with this command:

For other nodes:

```docker run -it -e PORT=800x -e IP=172.18.0.y -p 800x:8000 --network ntua-blockchain_blockchat --rm ntua-blockchain```