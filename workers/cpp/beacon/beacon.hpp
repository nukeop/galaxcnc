#include <string>

/*
  Simple worker that broadcasts the ip of the machine it's running on every minute.
  Compilable to a single binary.
 */

class Beacon
{
public:
  // Constructors/destructors
  Beacon(){};
  Beacon(char* nick, char* channel);
  virtual ~Beacon();

  // Methods
  void run();
  void getExternalIp(char** out);

protected:
  // Members
  unsigned char* m_publicKey;
  unsigned int m_delay;
  char* m_nickname;
  char* m_channel;
  bool m_isConnected;
  bool m_isJoined;

  // Methods
  void init();

private:
  // Members
  char *m_port;
  int m_socket;

  // Methods
  char* timeNow();
  bool sendData(char* msg);
  bool charSearch(char* toSearch, char* term);
  void sendPong(char* buf);
  void msgHandle(char* buf);
};
