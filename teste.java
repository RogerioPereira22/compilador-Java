int main() {
    int numBloco_0, divBloco_0, restoBloco_0;
    system.out.print("Entre com o inteiro: ");
    system.in.scan(int, numBloco_0);
    system.out.print(int,"=", numBloco_0);

    while (numBloco_0 > 1) {
        divBloco_0 = 2;
        while (1) {
            restoBloco_0 = numBloco_0 % divBloco_0;
            if (restoBloco_0 == 0) {
                break;
            }
            divBloco_0++;
        }
        system.out.print(int, divBloco_0);
        numBloco_0 /= divBloco_0;
        if (numBloco_0 > 1) {
             system.out.print(" * ");
        }
    }
    system.out.print("\n");
}