from django.db import models

class Raffle(models.Model):
    post_id = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=255)
    num_spots = models.IntegerField()
    price_per_spot = models.DecimalField(max_digits=6, decimal_places=2)
    winning_spot = models.IntegerField()
    num_spots_for_winner = models.IntegerField()
    datetime_posted = models.DateTimeField()
    datetime_completed = models.DateTimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2)
    tier = models.IntegerField()
    url = models.TextField(default=None, blank=True, null=True)

    def get_spot_count_histogram(self):
        hist = ""
        for obj in SpotCount.objects.filter(post_id=self.post_id).order_by('num_spots'):
            hist += str(obj.num_spots) + ":" + str(obj.count) + ";"

        return hist


class SpotCount(models.Model):
    post_id = models.ForeignKey(Raffle, on_delete=models.CASCADE)
    num_spots = models.IntegerField()
    count = models.IntegerField()

    class Meta:
        unique_together = ("post_id", "num_spots")
