#Wyczyszczenie starych reguł
iptables -t filter -F
iptables -t filter -P INPUT ACCEPT

#Zezwalać na dowolne połączenia wychodzące.
iptables -t filter -P OUTPUT ACCEPT

#Zezwalać na połączenia przychodzące tylko pod warunkiem, że sami je inicjujemy.
iptables -t filter -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT

#Zezwalać na przychodzące połączenia inicjujące tylko na porty 80, 9000-9010.
#(Dla celów testowania na serwerze powinny być uruchomione serwery ssh oraz http).
iptables -t filter -A INPUT -p tcp -m state --state NEW -m multiport --dports 80,9000:9010 -j ACCEPT
iptables -t filter -A INPUT -p udp -m state --state NEW -m multiport --dports 80,9000:9010 -j ACCEPT

#Wpuszczać żądania echa ICMP.
iptables -t filter -A INPUT -p icmp --icmp-type 8 -j ACCEPT

#Zezwalać na połączenia inicjujące ssh tylko z podsieci BSK lab.
#Ograniczyć liczbę połączeń inicjujących przychodzących do portu 22 do 10 na minutę
#z jednego źródłowego adresu IP.
iptables -t filter -A INPUT -p tcp -s 192.168.1.0/24 -m state --state NEW -m hashlimit --hashlimit-name foo --hashlimit-mode srcip --hashlimit-upto 10/minute --dport 22 -j ACCEPT

#TODO sprawdzic nazwe interfejsu
#Zadbać o interfejs loopback.
iptables -t filter -A INPUT -i lo -j ACCEPT

#Przygotować regułę/reguły firewalla umożliwiające uruchomienie podstawowego serwera DNS.
iptables -t filter -A INPUT -p udp -s 192.168.1.0/24 -m state --state NEW --dport 53 -j ACCEPT
iptables -t filter -A INPUT -p tcp -s 192.168.1.0/24 -m state --state NEW --dport 53 -j ACCEPT

#Blokować wszystkie inne połączenia przychodzące.
iptables -t filter -P INPUT DROP

