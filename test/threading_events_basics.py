#def A():
#"""
#Thread A
#"""
#    while True:
#        time.sleep(3)
#        if event.is_set():
#            print("A sees event is set!")
#            event.wait()
#            print("A wait is finished")
#        else:
#            print("A says event not set")
#            if random.random() > 0.66:
#                print("A decided to SET the event")
#                event.set()


#def B():
#"""
#Thread B
#"""
#    while True:
#        time.sleep(6)
#        if not event.is_set():
#            print("B sees event is not set!")
#        else:
#            print("B says event is set")
#            if random.random() > 0.66:
#                print("B decided to CLEAR the event")
#                event.clear()
#                print("B is now going to wait")
#                event.wait()

#event = Event()

#x = Thread(target=A)
#y = Thread(target=B)

#x.start()
#y.start()
