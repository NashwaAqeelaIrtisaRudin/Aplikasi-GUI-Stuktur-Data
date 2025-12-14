"""
Data Structure Models for Music Player Application
Contains all data structures used for managing songs, playlists, queues, and history.
"""

import collections


class Lagu:
    """Represents a song with its metadata and file path."""
    
    def __init__(self, id_lagu, judul, artis, album, genre, tahun, file_path=None):
        self.id = id_lagu
        self.judul = judul
        self.artis = artis
        self.album = album
        self.genre = genre
        self.tahun = tahun
        self.file_path = file_path  # Path to audio file

    def __str__(self):
        return f"{self.judul} - {self.artis}"

    def __repr__(self):
        return f"Lagu(id='{self.id}', judul='{self.judul}', artis='{self.artis}', album='{self.album}', genre='{self.genre}', tahun={self.tahun}, file_path='{self.file_path}')"




class NodeLagu:
    """Node for SinglyLinkedList containing a Song."""
    def __init__(self, lagu):
        self.data = lagu
        self.next = None


class SinglyLinkedList:
    """Singly linked list implementation for the music library."""
    
    def __init__(self):
        self.head = None
        self.size = 0

    def append(self, lagu):
        """Add a song to the end of the list."""
        new_node = NodeLagu(lagu)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1

    def remove_by_id(self, id_lagu):
        """Remove a song by its ID and return it."""
        current = self.head
        previous = None
        while current:
            if current.data.id == id_lagu:
                if previous:
                    previous.next = current.next
                else:
                    self.head = current.next
                self.size -= 1
                return current.data
            previous = current
            current = current.next
        return None

    def find_by_id(self, id_lagu):
        """Find a song by its ID."""
        current = self.head
        while current:
            if current.data.id == id_lagu:
                return current.data
            current = current.next
        return None

    def find_by_criteria(self, **kwargs):
        """Find songs matching the given criteria."""
        results = []
        current = self.head
        while current:
            match = True
            for key, value in kwargs.items():
                if not hasattr(current.data, key) or getattr(current.data, key) != value:
                    match = False
                    break
            if match:
                results.append(current.data)
            current = current.next
        return results

    def display(self):
        """Display all songs in the list."""
        current = self.head
        while current:
            print(current.data)
            current = current.next

    def get_all_lagu(self):
        """Get all songs as a Python list."""
        lagu_list = []
        current = self.head
        while current:
            lagu_list.append(current.data)
            current = current.next
        return lagu_list


class NodePlaylist:
    """Node for doubly linked list containing a song in a playlist."""
    def __init__(self, lagu):
        self.data = lagu
        self.next = None
        self.prev = None


class DoublyLinkedList:
    """Doubly linked list implementation for playlists."""
    
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, lagu):
        """Add a song to the end of the playlist."""
        new_node = NodePlaylist(lagu)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def remove_node(self, node):
        """Remove a specific node from the playlist."""
        if not node:
            return
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        self.size -= 1

    def find_node_by_lagu_id(self, id_lagu):
        """Find a node by song ID."""
        current = self.head
        while current:
            if current.data.id == id_lagu:
                return current
            current = current.next
        return None

    def display(self):
        """Display all songs in the playlist."""
        current = self.head
        while current:
            print(current.data)
            current = current.next

    def get_as_list(self):
        """Get all songs as a Python list."""
        lagu_list = []
        current = self.head
        while current:
            lagu_list.append(current.data)
            current = current.next
        return lagu_list


class Queue:
    """Queue implementation for playback queue (FIFO)."""
    
    def __init__(self):
        self.items = collections.deque()

    def enqueue(self, item):
        """Add an item to the queue."""
        self.items.append(item)

    def dequeue(self):
        """Remove and return the first item from the queue."""
        if not self.is_empty():
            return self.items.popleft()
        return None

    def is_empty(self):
        """Check if the queue is empty."""
        return len(self.items) == 0

    def size(self):
        """Get the size of the queue."""
        return len(self.items)

    def peek(self):
        """View the first item without removing it."""
        if not self.is_empty():
            return self.items[0]
        return None


class Stack:
    """Stack implementation for playback history (LIFO)."""
    
    def __init__(self):
        self.items = []

    def push(self, item):
        """Push an item onto the stack."""
        self.items.append(item)

    def pop(self):
        """Pop and return the top item from the stack."""
        if not self.is_empty():
            return self.items.pop()
        return None

    def is_empty(self):
        """Check if the stack is empty."""
        return len(self.items) == 0

    def peek(self):
        """View the top item without removing it."""
        if not self.is_empty():
            return self.items[-1]
        return None

    def size(self):
        """Get the size of the stack."""
        return len(self.items)
