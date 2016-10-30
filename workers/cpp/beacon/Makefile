CPP=g++
CPPFLAGS= -std=c++11 -ggdb -w
SOURCES=beacon.cpp
LIBS= -lcurl
OBJECTS=$(SOURCES:.cpp=.o)
EXE=beacon

all: $(SOURCES) $(EXE)

$(EXE): $(OBJECTS)
	$(CPP) $(OBJECTS) $(LIBS) -o $@

.cpp.o:
	$(CPP) $(CPPFLAGS) -c $*.cpp

clean:
	rm beacon
	rm *.o
