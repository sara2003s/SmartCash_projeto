from django.db import models 
from django.contrib.auth.models import User
from django.utils import timezone
	
class Meta:
    ordering = ['-data']

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    cor = models.CharField(max_length=7, default="#000000") 

    def __str__(self):
           return self.nome

class Transacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=[('entrada', 'Entrada'), ('saida', 'Saída')])
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    data = models.DateField(default=timezone.now)
    
def __str__(self):
		return f"{self.nome} - {self.valor} ({self.tipo}) em {self.data}"