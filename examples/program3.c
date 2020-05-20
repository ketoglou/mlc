//This code is for testing the idermediate language of minimal++

#include <stdio.h>


int testBlocks(){
	L_1:asm("nop");//1:begin_block,fun1,_,_
	int a,b,c,d,T_0,T_1,T_2,T_3,T_4,T_5,T_6,T_7;
	L_2: a = 1;	//2::=,1,_,a
	L_3: return a;	//3:retv,a,_,_
	L_4: asm("nop");	//4:end_block,fun1,_,_
}

int fun1(){
	L_5:asm("nop");//5:begin_block,fun1,_,_
	int a;
	L_6: asm("nop");	//par,a,CV,_
	L_7: asm("nop");	//par,T_0,RET,_
	L_8: T_0 = fun1(a);	//call,fun1,_,_
	L_9: a = T_0;	//9::=,T_0,_,a
	L_10: asm("nop");	//par,T_1,RET,_
	L_11: T_1 = fun1();	//call,fun1,_,_
	L_12: a = T_1;	//12::=,T_1,_,a
	L_13: T_2 = 1;	//13::=,1,_,T_2
	L_14: T_2 = T_2 + v;	//14:+,T_2,v,T_2
	L_15: a = T_2;	//15::=,T_2,_,a
	L_16: return a;	//16:retv,a,_,_
	L_17: asm("nop");	//17:end_block,fun1,_,_
}

int fun1(int v){
	L_18:asm("nop");//18:begin_block,block4,_,_
	int a,T_0,T_1,T_2;
	L_19: asm("nop");	//par,k,CV,_
	L_20: asm("nop");	//par,T_0,RET,_
	L_21: T_0 = block2(k);	//call,block2,_,_
	L_22: a = T_0;	//22::=,T_0,_,a
	L_23: return k;	//23:retv,k,_,_
	L_24: asm("nop");	//24:end_block,block4,_,_
}

void block1(int *a, int *b, int c){
	L_25:asm("nop");//25:begin_block,block3,_,_
		L_26: asm("nop");	//26:end_block,block3,_,_
}

int block2(int z){
	L_27:asm("nop");//27:begin_block,block2,_,_
	int e,f,g;
	L_28: return 2;	//28:retv,2,_,_
	L_29: asm("nop");	//29:end_block,block2,_,_
}

void block3(){
	L_30:asm("nop");//30:begin_block,block5,_,_
		L_31: asm("nop");	//par,a,REF,_
	L_32: asm("nop");	//par,b,REF,_
	L_33: asm("nop");	//par,3,CV,_
	L_34: block1(&a,&b,3);	//call,block1,_,_
	L_35: asm("nop");	//par,a,CV,_
	L_36: asm("nop");	//par,T_0,RET,_
	L_37: T_0 = block2(a);	//call,block2,_,_
	L_38: a = T_0;	//38::=,T_0,_,a
	L_39: asm("nop");	//par,a,CV,_
	L_40: asm("nop");	//par,T_1,RET,_
	L_41: T_1 = fun1(a);	//call,fun1,_,_
	L_42: a = T_1;	//42::=,T_1,_,a
	L_43: asm("nop");	//43:end_block,block5,_,_
}

int block4(int k){
	L_44:asm("nop");//44:begin_block,block1,_,_
	int T_0;
	L_45: asm("nop");	//45:end_block,block1,_,_
}

void block5(int a, int b){
	L_46:asm("nop");//46:begin_block,testBlocks,_,_
	int T_0,T_1;
	L_47: asm("nop");	//par,a,REF,_
	L_48: asm("nop");	//par,b,REF,_
	L_49: c(&a,&b);	//:=,c,_,T_0
	L_50: T_0 = T_0 - 1;	//50:-,T_0,1,T_0
	L_51: asm("nop");	//par,T_0,CV,_
	L_52: block1(T_0);	//call,block1,_,_
	L_53: T_1 = 3;	//53::=,3,_,T_1
	L_54: T_1 = T_1 + a;	//54:+,T_1,a,T_1
	L_55: T_1 = T_1 + b;	//55:+,T_1,b,T_1
	L_56: T_2 = 23;	//56::=,23,_,T_2
	L_57: T_2 = T_2 * 8;	//57:*,T_2,8,T_2
	L_58: T_1 = T_1 - T_2;	//58:-,T_1,T_2,T_1
	L_59: T_3 = b;	//59::=,b,_,T_3
	L_60: T_3 = T_3 / 2;	//60:/,T_3,2,T_3
	L_61: T_3 = T_3 * 3533;	//61:*,T_3,3533,T_3
	L_62: T_1 = T_1 + T_3;	//62:+,T_1,T_3,T_1
	L_63: d = T_1;	//63::=,T_1,_,d
	L_64: printf("%d\n",d);	//64:out,d,_,_
	L_65: T_4 = a;	//65::=,a,_,T_4
	L_66: T_4 = T_4 + 2;	//66:+,T_4,2,T_4
	L_67: T_4 = T_4 + b;	//67:+,T_4,b,T_4
	L_68: T_5 = c;	//68::=,c,_,T_5
	L_69: T_5 = T_5 + 3;	//69:+,T_5,3,T_5
	L_70: T_5 = T_5 + d;	//70:+,T_5,d,T_5
	L_71: T_4 = T_4 + T_5;	//71:+,T_4,T_5,T_4
	L_72: T_4 = T_4 + c;	//72:+,T_4,c,T_4
	L_73: c = T_4;	//73::=,T_4,_,c
	L_74: scanf("%d",&a);	//74:inp,a,_,_
	L_75: T_6 = 1;	//75::=,1,_,T_6
	L_76: asm("nop");	//par,T_7,RET,_
	L_77: T_7 = fun1();	//call,fun1,_,_
	L_78: T_6 = T_6 + T_7;	//78:+,T_6,T_7,T_6
	L_79: c = T_6;	//79::=,T_6,_,c
	L_80: return 0;	//80:halt,_,_,_
	L_81: asm("nop");	//81:end_block,testBlocks,_,_
}


int main(){
	 return block5();
}