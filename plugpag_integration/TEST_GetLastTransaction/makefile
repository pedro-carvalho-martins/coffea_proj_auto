INCS = -I./include 
OUTDIR = ./output
OBJS = $(OUTDIR)/get_last_payment_plugpag.o 
LIBS = -lPPPagSeguro -lBTSerial -ldl

all: $(OUTDIR)/get_last_payment_plugpag

clean: 
	rm -r $(OBJS) $(OUTDIR)/get_last_payment_plugpag $(OUTDIR)

$(OUTDIR)/get_last_payment_plugpag: main
	gcc  -o $(OUTDIR)/get_last_payment_plugpag $(OBJS) $(LIBS)
	
main:
	mkdir -p $(OUTDIR)
	gcc -D__linux__ $(INCS)  -g3 -Wall -c get_last_payment_plugpag.c -o $(OUTDIR)/get_last_payment_plugpag.o

