int x = 3;

int main(){
    printf("El señor %s es un individuo %s, %s y con %d %s.", "Manolo", "tranquilo", "trabajador", 48, "anos");
    int x = 0;

    if(x){
        x = 20;
        return x;
    }else{
        x = 8;

        int y = 4;
        printf("Introduce un numero entero: ");
        int z;
        scanf("%d", &z);
        printf("z = %d", z);
        printf("x = %d", x);    
        return 15;
    }

    printf("Retornamos 18");
    return 18;
}
