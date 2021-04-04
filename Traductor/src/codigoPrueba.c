int x = 3;
int y;

int fact(int n) {
    int acum = 1;

    while (n > 1){
        printf("n = %d",n);
        acum = acum * n;
        n = n - 1;
    }

    return acum;
}

int main(){
    y = 4;
    // z = 17; // Comentado porque daría error si no lo estuviera

    int x = 5;
    return fact(y);
}
