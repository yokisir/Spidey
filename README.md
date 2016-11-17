# Spidey
System of auto-detect and collect Malicious URLs

---
###Development environment
* Windows 10 (have not test in linux or other windows version)
* Python 2.7.11
* Django 1.11.0 (alpha)
* MySQL 5.6.24

###Function
Based on the thorough research on the actual needs of users, a malicious web site detection method combining anti-virus software call and static detection is proposed, and a real-time automatic detection and collection system of malicious web site is realized. The system proactively detects the URLs obtained from third-party exposure stations and third-party search engines, classifies the URLs and stores them in the database for users to analyze the malicious degree of the websites and configure the firewalls as safe operation. It is found that the system runs stably and has high accuracy. It can effectively collect malicious web addresses in the network and regularly update its malicious URL database.
