# we_love_p2p
一个简单的p2p文件共享与同步系统



Server：tracker程序

Client：各个节点的程序





其中server上部署在一台具有公网ip的服务器上，用来存储各个节点的信息并广播IP信息，带有记录每个块(chunk)发出、到达和本地每个文件完整收到的时间



各个节点运行client中程序，用来接入p2p网络，以及实现共享文件夹的同步与协商删除的功能

