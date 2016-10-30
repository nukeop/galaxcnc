#include <iostream>
#include <sstream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <curl/curl.h>

#include "beacon.hpp"

Beacon::Beacon(char* nick, char* channel)
{
  m_nickname = nick;
  m_channel = channel;
  m_port = "6667";
  init();
}

Beacon::~Beacon()
{
  close(m_socket);
}

void Beacon::init()
{
  struct addrinfo hints, *servinfo;
  memset(&hints, 0, sizeof hints);
  hints.ai_family = AF_INET;
  hints.ai_socktype = SOCK_STREAM;

  int res;
  if((res = getaddrinfo("chat.freenode.net", m_port, &hints, &servinfo)) != 0)
    {
      printf("Could not create addrinfo");
      exit(-1);
    }

  if ((m_socket = socket(servinfo->ai_family, servinfo->ai_socktype, servinfo->ai_protocol)) == -1)
    {
      printf("Could not setup the socket");
      exit(-1);
    }

  if (connect(m_socket, servinfo->ai_addr, servinfo->ai_addrlen) == -1)
    {
      close(m_socket);
      printf("Unable to connect");
      exit(-1);
    }

  m_isConnected = true;

  freeaddrinfo(servinfo);
}

void Beacon::run()
{
  int numbytes;
  char buf[100];
  int count = 0;

  char* curIp;
  getExternalIp(&curIp);

  // Establish and setup a connection
  while(!m_isJoined)
    {
      count++;
      if(count == 3)
        {
          std::stringstream ss;

          //Build and send nickname
          ss.str(std::string());
          ss << "NICK " << m_nickname << "\r\n";
          const char* msgconstnick = ss.str().c_str();
          char* msgnick = new char[strlen(msgconstnick) + 1];
          strcpy(msgnick, msgconstnick);

          sendData(msgnick);
        }

      if(count==4)
        {
          std::stringstream ss;

          // Build and send username
          ss.str(std::string());
          ss << "USER " << m_nickname << " 8 * " << m_nickname << "\r\n";
          const char* msgconst = ss.str().c_str();
          char* msg = new char[strlen(msgconst) + 1];
          strcpy(msg, msgconst);

          sendData(msg);
        }

      if(charSearch(buf, "MOTD"))
        {
          std::stringstream ss;
          ss << "JOIN " << m_channel << "\r\n";
          const char* msgconst = ss.str().c_str();
          char* cmsg = new char[strlen(msgconst) + 1];
          strcpy(cmsg, msgconst);
          sendData(cmsg);
          m_isJoined = true;
        }

      numbytes = recv(m_socket, buf, 99, 0);
      buf[numbytes]=0;
      std::cout << buf;
      msgHandle(buf);

      if(charSearch(buf, "PING"))
        {
          sendPong(buf);
        }

      if(numbytes==0)
        {
          std::cout << "Connection closed" << std::endl;
          std::cout << timeNow() << std::endl;
          break;
        }
    }

  printf("\n\nEntering main loop\n\n");

  while(true)
    {
      std::stringstream ss;
      ss << "PRIVMSG " << m_channel << " : My IP is:" << curIp << "\r\n";
      const char* msgconst = ss.str().c_str();
      char* cmsg = new char[strlen(msgconst) + 1];
      strcpy(cmsg, msgconst);
      sendData(cmsg);


      if(charSearch(buf, "PING"))
        {
          sendPong(buf);
        }

      if(numbytes==0)
        {
          std::cout << "Connection closed" << std::endl;
          std::cout << timeNow() << std::endl;
          break;
        }

      sleep(5);
    }
}

bool Beacon::sendData(char* msg)
{
  int len = strlen(msg);
  int bytes_sent = send(m_socket, msg, len, 0);
  if (bytes_sent==0)
    return false;
  else
    return true;
}

bool Beacon::charSearch(char* toSearch, char* term)
{
  int len = strlen(toSearch);
  int termLen = strlen(term);

  for (int i=0; i<len; i++)
    {
      if (term[0] == toSearch[i])
        {
          bool found = true;
          for(int x=1; x<termLen; x++)
            {
              if(toSearch[i+x]!=term[x])
                {
                  found=false;
                  break;
                }
            }
          return found;
        }
    }
  return false;
}

void Beacon::sendPong(char* buf)
{
  int buflen = strlen(buf);
  char reply [buflen];
  for (int i=0; i < buflen; i++)
    {
      reply[i] = buf[i];
    }
  reply[1] = 'O';
  if(sendData(reply))
    {
      std::cout << timeNow() << " ping pong" << std::endl;
    }
}

char* Beacon::timeNow()
{
  time_t rawtime;
  struct tm* timeinfo;
  time(&rawtime);
  timeinfo = localtime(&rawtime);
  return asctime(timeinfo);
}

void Beacon::msgHandle(char* buf)
{
  // Does nothing, we just ignore messages
}

size_t static curl_write_callback_func(void *buffer,
                                       size_t size,
                                       size_t nmemb,
                                       void *userp)
{
  char **response_ptr =  (char**)userp;
  *response_ptr = strndup((char*)buffer, (size_t)(size *nmemb));
}

void Beacon::getExternalIp(char** out)
{
  CURL* curl;
  CURLcode res;
  char* ipstr;
  curl = curl_easy_init();
  curl_easy_setopt(curl, CURLOPT_URL, "https://api.ipify.org");
  curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, curl_write_callback_func);
  curl_easy_setopt(curl, CURLOPT_WRITEDATA, &ipstr);
  curl_easy_perform(curl);

  curl_easy_cleanup(curl);

  *out = strdup(ipstr);
}


int main()
{
  Beacon* b = new Beacon("ahgfEoGWEg", "#YIKjkXYorK");

  b->run();
  return 0;
}
