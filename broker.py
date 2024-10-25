import zmq
import sys

def broker(frontend_port="5050", backend_port="5051"):
    context = zmq.Context()

    # Socket XSUB para recibir de los publicadores (taxis)
    frontend = context.socket(zmq.XSUB)
    frontend.bind(f"tcp://*:{frontend_port}")

    # Socket XPUB para enviar a los subscriptores (servidor)
    backend = context.socket(zmq.XPUB)
    backend.bind(f"tcp://*:{backend_port}")

    print(f"Broker iniciado. Enrutando mensajes entre taxis en {frontend_port} y servidor en {backend_port}.")

    try:
        # Proxy para enrutar mensajes entre XSUB y XPUB
        zmq.proxy(frontend, backend)
    except KeyboardInterrupt:
        print("\nBroker interrumpido. Cerrando...")
    except Exception as e:
        print(f"Error en el broker: {e}")
    finally:
        frontend.close()
        backend.close()
        context.term()
        print("Broker cerrado.")

if __name__ == "__main__":
    frontend_port = sys.argv[1] if len(sys.argv) > 1 else "5050"
    backend_port = sys.argv[2] if len(sys.argv) > 2 else "5051"
    broker(frontend_port, backend_port)