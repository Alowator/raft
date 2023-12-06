class LockProvider:
    UNLOCK_TIME = 10

    def __init__(self):
        self._locks = {}

    def acquire(self, lockID, clientID, currentTime):
        existingLock = self._locks.get(lockID, None)
        # Auto-unlock old lock
        if existingLock is not None:
            if currentTime - existingLock[1] > self.UNLOCK_TIME:
                existingLock = None
        # Acquire lock if possible
        if existingLock is None or existingLock[0] == clientID:
            self._locks[lockID] = (clientID, currentTime)
            return True
        # Lock already acquired by someone else
        return False

    def prolongate(self, clientID, currentTime):
        for lockID in list(self._locks):
            lockClientID, lockTime = self._locks[lockID]

            if currentTime - lockTime > self.UNLOCK_TIME:
                del self._locks[lockID]
                continue

            if lockClientID == clientID:
                self._locks[lockID] = (clientID, currentTime)

    def release(self, lockID, clientID):
        existingLock = self._locks.get(lockID, None)
        if existingLock is not None and existingLock[0] == clientID:
            del self._locks[lockID]

    def isAcquired(self, lockID, clientID, currentTime):
        existingLock = self._locks.get(lockID, None)
        if existingLock is not None:
            if existingLock[0] == clientID:
                if currentTime - existingLock[1] < self.UNLOCK_TIME:
                    return True
        return False
