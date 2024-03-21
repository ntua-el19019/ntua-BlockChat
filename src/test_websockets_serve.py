import asyncio
import os
import json
import websockets
from dotenv import load_dotenv
from nodes import Node
from block import Block
from transaction import Transaction
from wsmanager import send_websocket_request
import execute_tests


lock = asyncio.Lock()

node = Node()

# Load environment variables and set up node details
load_dotenv()
IP_ADDRESS = os.getenv("IP", "172.18.0.2")
PORT = os.getenv("PORT", 8000)
total_nodes = int(os.getenv('TOTAL_NODES', 3))
total_bcc = total_nodes * 1000
block_capacity = int(os.getenv('BLOCK_CAPACITY', 5))
test_mode = bool(os.getenv('TEST_MODE', False))

bootstrap_node = {
    'ip': os.getenv('BOOTSTRAP_IP', '172.18.0.2'),
    'port': os.getenv('BOOTSTRAP_PORT', '8000')
}

# Debug prints
print('IP address: ', IP_ADDRESS)
print('PORT: ', PORT)

node.ip = IP_ADDRESS
node.port = str(PORT)



# See if node is Bootstrap node
if IP_ADDRESS == bootstrap_node["ip"] and str(PORT) == bootstrap_node["port"]:
    node.id = 0
    bootstrap_node = node
    print("I am bootstrap")

# node.initialization_event = asyncio.Event()

#bootstrap_ready_event = asyncio.Event()
# Register node to the cluster
bootstrap_ready_event = asyncio.Event()
test_ready_event = asyncio.Event()
async def register_node():
    #global bootstrap_ready_event
    # bootstrap_ready_event = asyncio.Condition()
    # async with bootstrap_ready_event:
        if node.id == 0:
            # Add himself to ring
            node.register_node_to_ring(node.id, node.ip, node.port, node.wallet.public_key)

            # print("Registered Bootstrap node to ring")  # print("Registered Bootstrap node to ring")
            transaction = Transaction(
                sender_address='0',
                receiver_address=node.wallet.public_key,
                type_of_transaction='coin',
                amount=total_bcc,
                nonce=1,
                message=None
            )
            
            # node.transaction_pool.append(transaction)
            node.wallet.balance += total_bcc

            # print("Genesis transaction added to transaction pool")
            genesis_block = Block(1,'1')
        
            genesis_block.validator = 0
            genesis_block.transactions.append(transaction)
            await node.chain.add_block(genesis_block,node)
            # node.current_block = Block(node.chain.blocks[-1].index + 1, node.chain.blocks[-1].current_hash)
            # print("Genesis block added to chain")
            print("Bootstrap node waiting for other nodes to be ready...")
            await bootstrap_ready_event.wait()
            #await bootstrap_ready_event.wait()
            print("Bootstrap node proceeding...")
            await send_init_bcc()
            #await node.send_initial_bcc()
            print('After send_initial_bcc')
            await test_ready_event.wait()
            if test_mode:
                await execute_tests.execute_transactions(node.id, node.ip, node.port)

        else: 
            # Gather all unicast tasks
            unicast_tasks = [node.unicast_node(bootstrap_node), send_websocket_request('init_account_space', {}, node.ip, node.port)]
            await asyncio.gather(*unicast_tasks)

            data = await send_websocket_request('get_ring_length', {}, node.ip, node.port)
            print("Ring length: ", data['ring_len'])
            if data['ring_len'] == total_nodes: #TODO: may need better condition
                await send_websocket_request('last_node_ready', {}, bootstrap_node['ip'], bootstrap_node['port'])
                # test_ready_event.set()
              

            await test_ready_event.wait()
            if test_mode:
                await execute_tests.execute_transactions(node.id, node.ip, node.port)
                # await execute_tests.execute_transactions()

    
async def send_init_bcc():
    print("Node ID in send initial: ", node.id)
    if node.id == 0:
        await node.send_initial_bcc()
        # node.initialization_event.set()

        """
        for node in self.ring :
                if self.id != node['id']:a
         
                     asyncio.create_task(self.send_transaction(node, transaction))
         
                
        for node in self.ring:
            if self.id == node['id']:
                 response = await self.send_transaction(node, transaction)
        """
        # await asyncio.sleep(1)
        # for ring_node in node.ring:
            # if ring_node['id'] != 0:
        await asyncio.sleep(3)
        for ring_node in node.ring:
            # if ring_node['id'] == 1:
                 asyncio.create_task(send_websocket_request('ready_for_tests', {}, ring_node['ip'], ring_node['port']))
                
        await send_websocket_request('ready_for_tests', {}, node.ip, node.port)
                
        # for ring_node in node.ring:
        #     if ring_node['id'] == 0:
        #         await send_websocket_request('execute_tests', {}, ring_node['ip'], ring_node['port'])
        


async def handler(websocket):
   

    async for message in websocket:
        data = json.loads(message)
        
        

        if data['action'] == 'last_node_ready':
            print("Last node is ready, proceeding...")
            bootstrap_ready_event.set()  # Signal the event
            await websocket.send(json.dumps({'message': "Last node is ready endpoint triggered"}))

        elif data['action'] == 'ready_for_tests':
            # await asyncio.sleep(1)
            test_ready_event.set()
            await websocket.send(json.dumps({'message': "Tests event set"}))
          
            # await websocket.send(json.dumps({'message': "Tests executed"}))
        

        elif data['action'] == 'register_node':
            node_data = data['data']
        
            bootstrap_node.register_node_to_ring(len(bootstrap_node.ring), node_data['ip'], node_data['port'], node_data['public_key'])

            if len(bootstrap_node.ring) == total_nodes:
                
                for ring_node in bootstrap_node.ring:
                    if ring_node['id'] != 0:
                        await bootstrap_node.share_chain(ring_node)
                        await bootstrap_node.share_ring(ring_node)
                        await bootstrap_node.share_account_space(ring_node)
                        
                        
                        

               
            await websocket.send(json.dumps({'status' : 'Node with id ' + str(len(bootstrap_node.ring)) + ' registered'}))

           
           

        elif data['action'] == 'new_transaction':
           
            receiver = data['data']['receiver']
            for ring_node in node.ring:
                if ring_node['id'] == int(receiver):
                    receiver = ring_node['public_key']
                    break

            amount = data['data']['amount']
          
            if await node.create_transaction(receiver, 'coin', amount):
              
                await websocket.send(json.dumps({'message': "Transaction created"}))
            else:
                await websocket.send(json.dumps({'message': "Transaction failed"}))

     
        elif data['action'] == 'new_message':
           
            receiver = data['data']['receiver']
            for ring_node in node.ring:
                if ring_node['id'] == int(receiver):
                    receiver = ring_node['public_key']
                    break

            
            message = data['data']['message']
            # Perform the transaction 
            if await node.create_transaction(receiver, 'message', 0, message):
                # Send back a JSON response
                await websocket.send(json.dumps({'message': "Message was registered"}))
            else:
                await websocket.send(json.dumps({'message': "Sending of the message failed"}))
        
        elif data['action'] == 'validate_transaction':
            new_transaction = data['transaction']
            if await node.validate_transaction(new_transaction):
                await websocket.send(json.dumps({'message': "OK"}))
            else:
                await websocket.send(json.dumps({'message': "The signature is not valid or not enough balance"}))

        elif data['action'] == 'get_balance':
            balance = node.account_space[node.wallet.public_key]['balance']
            stake_amount = node.account_space[node.wallet.public_key]['stake']
            confirmed_balance = node.wallet.balance
            confirmed_stake = node.stake_amount
            #balance = node.wallet.balance
            wallet_address = node.wallet.public_key
            node_id = node.id

            await websocket.send(json.dumps({'Node ID':node_id,'chain':node.chain.to_dict(),'wallet_address':wallet_address,'balance': balance, 'stake':stake_amount, 'confirmed_balance':confirmed_balance, 'confirmed_stake':confirmed_stake}))

        elif data['action'] == 'view_last_transactions':
            last_validated_block = node.chain.blocks[-1].view_block()
            await websocket.send(json.dumps(last_validated_block))

        #elif data['action'] == ''

        elif data['action'] == 'view_last_messages':
            last_validated_block = node.chain.blocks[-1].view_block()
            messages = [transaction['message'] for transaction in last_validated_block['transactions'] if transaction['type_of_transaction'] == 'message' and transaction['recipient_address'] == node.wallet.public_key]
            await websocket.send(json.dumps(messages))
          

        elif data['action'] == 'get_ring_length':
            await websocket.send(json.dumps({'ring_len': len(node.ring)}))

   

        elif data['action'] == 'update_soft_state':
            node.account_space = data['data']
            print(f"Node {node.id} received 'update_soft_state' action")
            await websocket.send(json.dumps({'message': "Soft state updated"}))


        elif data['action'] == 'update_ring':
            new_ring = data['data']
            node.ring = new_ring

            for ring_node in node.ring:
                if ring_node['ip']==node.ip and ring_node['port']==node.port:
                    node.id = ring_node['id']
                    break   
            # print(f"Node {node.id} received 'update_ring' action")

            await websocket.send(json.dumps({'message': "Ring updated"}))



        elif data['action'] == 'init_account_space':

            #Only run from non-bootstrap nodes
            for ring_node in node.ring:
                if ring_node['id'] == 0:
                    node.account_space[ring_node['public_key']] = {
                        'ip': ring_node['ip'],
                        'id': ring_node['id'],
                        'port': ring_node['port'],
                        'balance': total_nodes * 1000,
                        'valid_balance': total_nodes * 1000,
                        'stake': 0,
                        'valid_stake': 0
                    }
                else:
                    node.account_space[ring_node['public_key']] = {
                        'ip': ring_node['ip'],
                        'id': ring_node['id'],
                        'port': ring_node['port'],
                        #'balance': 1000,
                        'balance': 0,
                        'valid_balance': 0,
                        'stake': 0,
                        'valid_stake': 0
                    }
            await websocket.send(json.dumps({'message': "Account space initialized"}))

        elif data['action'] == 'update_chain':
           
            # Get the serialized chain from the other node
            serialized_chain = data['data']
            # Deserialize the chain
            chain = node.chain.from_dict(serialized_chain)
            node.chain = chain
          

            await websocket.send(json.dumps({'message': "Chain updated"}))

        elif data['action'] == 'stake':
            amount = data['data']['amount']
            if await node.stake(amount):
                await websocket.send(json.dumps({'message': f"Pending stake: {amount}"}))
            else:
                await websocket.send(json.dumps({'message': "Failed to reserve amount for staking"}))

        elif data['action'] == 'get_stake':
            await websocket.send(json.dumps({'stake': node.stake_amount}))


     
        
        elif data['action'] == 'receive_transactions':
          
            transaction = data['data']
            print("I am in 'receive_transactions'")


            if node.current_block is None:
                node.current_block = Block(node.chain.blocks[-1].index + 1, node.chain.blocks[-1].current_hash)
         

            # if await node.validate_transaction(Transaction.from_dict(transaction)):
              
            transaction = Transaction.from_dict(transaction)
            # node.pending_transactions.append(transaction)
            #node.transaction_pool.append(transaction)
            res = await node.add_transaction_to_block(transaction)

            
            if res['status'] == 200 and res['message'] == 'Block is full and going to mint':
                #  await websocket.send(json.dumps({'valid':True,'message':'Block is full'}))
                    await node.mint_block()
                    await websocket.send(json.dumps(res))
                #  await websocket.send(json.dumps({'valid':True,'message':'Block is full'}))
            else:
                await websocket.send(json.dumps(res))
       

                    
            # else:
            #     # if Transaction.from_dict(transaction) in node.pending_transactions:
            #     #     node.pending_transactions.remove(Transaction.from_dict(transaction))
            #     await websocket.send(json.dumps({'message':'Transaction Invalid'}))
                
        


        elif data['action'] == 'new_block':
                # if node.chain.blocks[-1].current_hash != data['data']['hash']:
                async with node.chain.blockchain_lock:
                    block = Block.from_dict(data['data'])
                    validator = await Block.from_dict(data['data']).select_validator(node)
                    print(f"##############THE VALIDATOR for {Block.from_dict(data['data']).index} IS {validator['id']}##############")
                    print(f"##############PREVIOUS HASH: {node.chain.blocks[-1].current_hash[:20]}##############")
                   
                    if block.index > len(node.chain.blocks)+1:
                    # If the block's index is higher than the blockchain length, add it to the buffer
                        node.block_buffer[block.index] = block
                        print(f"##############BLOCK with {block.index} BUFFERED##############")

                    else:
                        if await node.validate_block(Block.from_dict(data['data'])):
                            print(f"########### NEW BLOCK RECEIVED with index {Block.from_dict(data['data']).index} ###########")
                            buff_blocks_added = await node.chain.add_block(Block.from_dict(data['data']),node)
                            buff_blocks_added.append(data['data'])

                            for buff_block in buff_blocks_added:    
                                await node.update_final_soft_state(buff_block)

                        
                            node.current_block = Block(node.chain.blocks[-1].index + 1, node.chain.blocks[-1].current_hash)
                        
                            for _ in range(block_capacity):
                                if not node.pending_transactions:
                                    break
                                trans = node.pending_transactions.popleft()
                                await node.add_transaction_to_block(trans)



                        
                         
                            await websocket.send(json.dumps({'status':200,'message':'Block added to chain', 'pk':node.wallet.public_key ,'new_balance':node.wallet.balance , 'new_stake':node.stake_amount}))



                        else:
                            if Block.from_dict(data['data']).previous_hash != node.chain.blocks[-1].current_hash:
                                print(f"#########BLOCK INVALID - HASH MISMATCH ###########")

                                # print(f"Expected previous hash: {node.chain.blocks[-1].previous_hash} but got {Block.from_dict(data['data']).previous_hash} ########")
                                # print(f"Last block index: {node.chain.blocks[-1].index} and received block index {Block.from_dict(data['data']).index}########")
                            elif Block.from_dict(data['data']).validator != (validator['pk']):
                                print(f"#########BLOCK INVALID VALIDATOR PROBLEM INDEX {Block.from_dict(data['data']).index} ###########")
                                # validator = await Block.from_dict(data['data']).select_validator(node)
                                print(f"Expected validator: {validator['pk']} but got {Block.from_dict(data['data']).validator} ########")
                        
                            await websocket.send(json.dumps({'status':400,'message':'Block Invalid'}))

        
      
                
        
        elif data['action'] == 'get_block_timestamps':
            timestamps = [block.current_hash[:20] for block in node.chain.blocks]
            await websocket.send(json.dumps({'timestamps':timestamps}))




# Start the WebSocket server

async def main():
    async with websockets.serve(handler, IP_ADDRESS, PORT,ping_interval=None):
        print(f"Server started at ws://{IP_ADDRESS}:{PORT}")
        
        await register_node()  # Register the node with the bootstrap node
        # asyncio.create_task(node.process_buffered_blocks())

        # await initialization_event.wait()
    
        # await execute_tests.execute_transactions()
     
        await asyncio.Future()  # This will keep the server running indefinitely

# Run the server
if __name__ == "__main__":
    
    asyncio.run(main())

                


