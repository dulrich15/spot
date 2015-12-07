# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0002_auto_20151207_0017'),
        ('core', '0011_auto_20151207_0017'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Student',
        ),
        migrations.AlterField(
            model_name='classroom',
            name='banner_filename',
            field=models.CharField(blank=True, max_length=200, null=True, choices=[('arm-wrestle.jpg', 'arm-wrestle.jpg'), ('billards-break.jpg', 'billards-break.jpg'), ('billiards-break.jpg', 'billiards-break.jpg'), ('black-hole-artistic.jpg', 'black-hole-artistic.jpg'), ('car-wreck-aftermath.jpg', 'car-wreck-aftermath.jpg'), ('clockwork-gears.jpg', 'clockwork-gears.jpg'), ('dali-persistence-of-memory.jpg', 'dali-persistence-of-memory.jpg'), ('dipole-radiation.jpg', 'dipole-radiation.jpg'), ('dipole-schematic.jpg', 'dipole-schematic.jpg'), ('electromagnetic-wave.png', 'electromagnetic-wave.png'), ('flame-thrower.jpg', 'flame-thrower.jpg'), ('flock-of-birds.jpg', 'flock-of-birds.jpg'), ('hoover-dam.jpg', 'hoover-dam.jpg'), ('hypnotic-spiral.jpg', 'hypnotic-spiral.jpg'), ('iphone.jpg', 'iphone.jpg'), ('lightning-bolts.jpg', 'lightning-bolts.jpg'), ('map-solar-system.jpg', 'map-solar-system.jpg'), ('mountain-scene.jpg', 'mountain-scene.jpg'), ('particle-tracks.jpg', 'particle-tracks.jpg'), ('peeling-out.jpg', 'peeling-out.jpg'), ('photoelasticity.png', 'photoelasticity.png'), ('power-lines-at-sunset.jpg', 'power-lines-at-sunset.jpg'), ('quantum-orbitals.jpg', 'quantum-orbitals.jpg'), ('rainbow.jpg', 'rainbow.jpg'), ('ripples-in-water.jpg', 'ripples-in-water.jpg'), ('scuba.png', 'scuba.png'), ('sharpening-knife.jpg', 'sharpening-knife.jpg'), ('simple-motor.jpg', 'simple-motor.jpg'), ('soap-bubbles.jpg', 'soap-bubbles.jpg'), ('spinning-top.jpg', 'spinning-top.jpg'), ('steam-engine.jpg', 'steam-engine.jpg'), ('stop-motion-biker-jump.jpg', 'stop-motion-biker-jump.jpg'), ('surface-of-sun.jpg', 'surface-of-sun.jpg'), ('swirling-light.jpg', 'swirling-light.jpg'), ('swirling-shampoo.jpg', 'swirling-shampoo.jpg'), ('target-practice.jpg', 'target-practice.jpg'), ('teeter-totter.png', 'teeter-totter.png'), ('touch', 'touch'), ('twisted-metal-beam.jpg', 'twisted-metal-beam.jpg'), ('very-hot-place.jpg', 'very-hot-place.jpg'), ('vibrating-strings.jpg', 'vibrating-strings.jpg'), ('vibration-abstract.png', 'vibration-abstract.png'), ('wave anatomy2.gif', 'wave anatomy2.gif')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='print_template',
            field=models.CharField(default='print_page.tex', max_length=256, editable=False, choices=[('print_page.tex', 'Page'), ('print_book.tex', 'Book'), ('print_book2.tex', 'Book2'), ('print_book_noindex.tex', 'book-noindex'), ('print_exam.tex', 'Exam'), ('print_equipment_form.tex', 'Equipment'), ('print_plain.tex', 'Plain')]),
            preserve_default=True,
        ),
    ]
