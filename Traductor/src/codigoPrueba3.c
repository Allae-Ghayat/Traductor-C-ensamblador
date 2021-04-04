void beeee(){
    printf("beeee");
}

int suma(int x, int y){
    int z = x + y;
    return z;
}

int fact(int n) {
    int acum = 1;
    printf("n = %d",n);

    while (n > 1){
        acum = acum * n;
        n = n - 1;
        printf("acum = %d",acum);
    }
    return acum;
}

int main(){
    beeee();
    int x = suma(2,3);
    return fact(x);
}
