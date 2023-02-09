INCS = -I./include 
OUTDIR = ./output
OBJS = $(OUTDIR)/payment_request_plugpag.o 
LIBS = -lPPPagSeguro -lBTSerial -ldl

all: $(OUTDIR)/payment_request_plugpag

clean: 
	rm -r $(OBJS) $(OUTDIR)/payment_request_plugpag $(OUTDIR)

$(OUTDIR)/payment_request_plugpag: main
	gcc  -o $(OUTDIR)/payment_request_plugpag $(OBJS) $(LIBS)
	
main:
	mkdir -p $(OUTDIR)
	gcc -D__linux__ $(INCS)  -g3 -Wall -c payment_request_plugpag.c -o $(OUTDIR)/payment_request_plugpag.o

