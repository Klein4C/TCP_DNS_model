Introduction to Each file and Basic Method of Using these Programmes
--------------------------------------------------------------------
General Rules:

	>>start 'com', 'gov' and 'org' server and root server before start using default server and client to get DNS;
	>>'^C' exception is used for server closing
	>>the 'com', 'gov' and 'org' servers were deliberatedly designed to pop timeout exception every 2 minutes.
	>>the 'com', 'gov' and 'org' servers thus need to be shut by keyboardexception manually
	>>please try to keep all the '.py' and '.dat' files under a same direction or the program may face error

--------------------------------------------------------------------
>file name:	client.py
>functionality:	provide interface for person to enter ID, URL and DNS method(I/R)
>feature:	only allow one try each time for protection of server and computer;
		will shutdown if timeout when waiting for reply;
		will shutsown of server shut down and send the 'shut' order here;
		will generate a [ID].log file each time and will cover old one if use a same ID;
>other: 	just follow the instruction on screen and enter the corresponding information

---------------------------------------------------------------------

>file name: 	server_default.py
>functionality:	work as a local default DNS server
>feature:	reveive primary request from client;
		multiple client supported;
		will keep record in 'server_default.log' each time it runs and replace old records if opened a new time;
		if DNS is successful, it will keep chached in 'mapping.logs' file;
		will deal with fundamental illegal format;
		when exited by keyboardexception, will send 'shut' order to all connected client and close self and clients;
>other:		please run this program before starting client to DNS

---------------------------------------------------------------------

>file name:	server_root.py
>functionality:	deal with iterating or recursive shoice;
		connect to the authority servers for address;
---------------------------------------------------------------------
>file name: 	server_com.py; server_gov.py; server_org.py
>functionality	final process to get IP address corresponding to the URL from database

