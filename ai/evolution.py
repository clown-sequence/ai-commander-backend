# backend/ai/evolution.py
import numpy as np
from typing import List, Dict

class BotGenome:
    def __init__(self):
        self.aggression = np.random.random()
        self.defense = np.random.random()
        self.cooperation = np.random.random()
        self.exploration = np.random.random()
        
    def mutate(self, rate=0.1):
        if np.random.random() < rate:
            self.aggression += np.random.normal(0, 0.1)
            self.aggression = np.clip(self.aggression, 0, 1)
        # ... mutate other traits ...
    
    def crossover(self, other):
        child = BotGenome()
        child.aggression = self.aggression if np.random.random() < 0.5 else other.aggression
        # ... crossover other traits ...
        return child

class Population:
    def __init__(self, size=50):
        self.genomes = [BotGenome() for _ in range(size)]
        self.fitness_scores = [0.0] * size
    
    def evaluate(self, game_results):
        """game_results: [{genome_id, kills, deaths, survival_time}, ...]"""
        for result in game_results:
            idx = result['genome_id']
            self.fitness_scores[idx] = (
                result['kills'] * 10 +
                result['survival_time'] * 0.1 -
                result['deaths'] * 5
            )
    
    def evolve(self):
        # Selection
        parents = self.tournament_selection(tournament_size=5)
        
        # Crossover
        children = []
        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                child = parents[i].crossover(parents[i+1])
                child.mutate()
                children.append(child)
        
        # Replace worst performers
        sorted_idx = np.argsort(self.fitness_scores)
        for i, child in enumerate(children):
            self.genomes[sorted_idx[i]] = child