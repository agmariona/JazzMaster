import math
import numpy as np

### PARAMETERS ###
D = 0.025
AGENT_INNER_WINDOW = 0.01
AGENT_OUTER_WINDOW = [-0.03, 0.03]
AGENT_MISS_PENALTY = 8

def cluster_intervals(events):
    clusters = []
    averages = np.empty((0,))
    for i in range(len(events)):
        for j in range(i+1, len(events)):
            interval = events[j] - events[i]
            if interval < D or interval > 2.5:
                continue
            try:
                k = np.argmin(np.abs(averages - interval))
            except ValueError:
                k = None

            if k is not None and np.abs(averages[k] - interval) < D:
                clusters[k].add(interval)
                averages[k] = clusters[k].average
            else:
                clusters.append(Cluster(interval))
                averages = np.append(averages, interval)

    merged_clusters = []
    deleted = []
    for i in range(len(clusters)):
        for j in range(i+1, len(clusters)):
            if j in deleted:
                continue
            if np.abs(clusters[i].average - clusters[j].average) < D:
                clusters[i].merge(clusters[j])
                deleted.append(j)
        merged_clusters.append(clusters[i])

    return merged_clusters

def is_close(a, b):
    return np.abs(a - b) < Agent.inner_window

def nearest_multiple(m, x):
    if m == 0:
        return x
    else:
        return math.floor((x / m) + 0.5) * m

def salience_mul(event):
    p = event[0]
    d = event[2]
    return d*(88-p)*np.log(np.e)

class Cluster:
    def __init__(self, interval):
        self.size = 1
        self.average = interval

    def add(self, interval):
        self.average = ((self.size*self.average)+interval) / (self.size+1)
        self.size += 1

    def merge(self, cluster):
        self.average = \
            ((self.size*self.average)+(cluster.size*cluster.average)) / \
            (self.size + cluster.size)
        self.size += cluster.size

class Agent:
    inner_window = AGENT_INNER_WINDOW
    outer_window = AGENT_OUTER_WINDOW
    penalty = AGENT_MISS_PENALTY
    n_agents = 0

    def __init__(self, tempo, phase, confidence=0):
        self.tempo = tempo
        self.phase = phase
        self.confidence = confidence
        self.history = []
        self.id = Agent.n_agents
        self.alive = True
        Agent.n_agents += 1

    def receive_event(self, event):
        onset = event[1]
        closest_beat = nearest_multiple(self.tempo, onset - self.phase) \
            + self.phase
        delta = onset - closest_beat
        if abs(delta) < Agent.inner_window:
            self.confidence += salience_mul(event)

            try:
                prev_onset = self.history[-1][1]
            except IndexError:
                self.history.append(event)
                return

            current_hit = nearest_multiple(self.tempo, onset - self.phase)
            prev_hit = nearest_multiple(self.tempo, prev_onset - self.phase)
            false_positives = (current_hit - prev_hit) // self.tempo - 1
            self.confidence -= false_positives * Agent.penalty

            self.phase = onset
            self.history.append(event)

        elif Agent.outer_window[0] < delta < Agent.outer_window[1]:
            return False

        if self.confidence < 0:
            self.alive = False

        return True

    def clone(self, event):
        onset = event[1]
        closest_beat = nearest_multiple(self.tempo, onset - self.phase) \
            + self.phase
        delta = onset - closest_beat
        assert Agent.outer_window[0] < delta < Agent.outer_window[1]
        clone = Agent(self.tempo, onset, confidence=self.confidence)
        clone.receive_event(event)
        return clone

    def __str__(self):
        return f'Agent {self.id}. Tempo: {1/self.tempo*60:.04}, ' + \
            f'Phase: {self.phase:.04}, Confidence: {self.confidence:.04}'

class BeatTracker:
    def __init__(self):
        self.agents = []
        self.clusters = []
        self.update_averages()
        pass

    def pass_events(self, events):
        onsets = [e[1] for e in events]
        new_cs = cluster_intervals(onsets)
        for_agents = []
        if len(self.clusters) == 0:
            self.clusters = new_cs
            for_agents += new_cs
        else:
            for new_c in new_cs:
                closest = self.clusters[
                    np.argmin(np.abs(self.averages - new_c.average))]
                if np.abs(new_c.average - closest.average) < D:
                    closest.merge(new_c)
                else:
                    self.clusters.append(new_c)
                    for_agents.append(new_c)
        self.update_averages()
        self.update_agents(events, for_agents)

    def update_averages(self):
        self.averages = np.array([c.average for c in self.clusters])

    def update_agents(self, events, for_agents):
        onsets = [e[1] for e in events]
        for c in for_agents:
            tempo = c.average
            self.agents.append(Agent(tempo, onsets[0]))
            pins = [onsets[0]]
            for e in onsets[1:]:
                for p in pins:
                    if is_close(e-p, nearest_multiple(tempo, e-p)):
                        break
                else:
                    self.agents.append(Agent(tempo, e))
                    pins.append(e)

        cloned_agents = []
        for agent in self.agents:
            if agent.alive:
                for e in events:
                    agent.receive_event(e)
                    if not agent.receive_event(e):
                        cloned_agents.append(agent.clone(e))
        self.agents = self.agents + cloned_agents

    def display_agents(self):
        for a in self.agents:
            print(a)

    def get_best_agent(self):
        return max(self.agents, key=lambda a: a.confidence)

    def get_tempo_phase(self):
        best = max(self.agents, key=lambda a: a.confidence)
        return best.tempo, best.phase
